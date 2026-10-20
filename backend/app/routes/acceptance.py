"""S-36: acceptance batches backed by SQLite, independently of S-26 defaults."""
import sqlite3
import uuid
from contextlib import closing
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from .auth import login_required, roles_required

acceptance = Blueprint("acceptance", __name__)


def connect():
    db = sqlite3.connect(current_app.config["USER_DATABASE"], timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def initialize(database_path):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.execute("PRAGMA foreign_keys=ON")
        db.executescript("""
            CREATE TABLE IF NOT EXISTS acceptance_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                batch_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','approved')),
                created_by INTEGER REFERENCES users(id),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS acceptance_lines (
                batch_id INTEGER NOT NULL REFERENCES acceptance_batches(id) ON DELETE CASCADE,
                task_id INTEGER NOT NULL REFERENCES cong_viec(id),
                cumulative TEXT NOT NULL,
                quantity TEXT NOT NULL,
                PRIMARY KEY (batch_id, task_id)
            );
            CREATE TABLE IF NOT EXISTS acceptance_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL REFERENCES acceptance_batches(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL
            );
        """)
        db.commit()


def decimal_number(value):
    if isinstance(value, bool) or value is None:
        raise ValueError('Khối lượng không hợp lệ.')
    try:
        n = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError('Khối lượng phải là số.') from None
    if not n.is_finite() or n < 0 or n > Decimal('999999999999'):
        raise ValueError('Khối lượng phải >= 0 và hữu hạn.')
    return n


def previous_approved(db, project, task_id, exclude=None):
    row = db.execute("""SELECT l.cumulative FROM acceptance_lines l
        JOIN acceptance_batches b ON b.id=l.batch_id
        WHERE b.project=? AND l.task_id=? AND b.status='approved'
          AND (? IS NULL OR b.id != ?)
        ORDER BY b.id DESC LIMIT 1""", (project, task_id, exclude, exclude)).fetchone()
    return Decimal(row['cumulative']) if row else Decimal('0')


def serialize_batch(db, batch):
    item = dict(batch)
    item['lines'] = [dict(line) for line in db.execute(
        'SELECT task_id,cumulative,quantity FROM acceptance_lines WHERE batch_id=? ORDER BY task_id', (batch['id'],))]
    item['images'] = [dict(image) for image in db.execute(
        'SELECT id,original_name FROM acceptance_images WHERE batch_id=?', (batch['id'],))]
    return item


@acceptance.get('/acceptance/tasks')
@login_required
def tasks():
    with closing(connect()) as db:
        rows = db.execute('SELECT id,ten,cong_trinh FROM cong_viec ORDER BY id').fetchall()
        # S-26 reports via getattr defaults, not persisted quantity fields. Never fabricate measured values.
        return jsonify([{**dict(row), 's26_measured': None} for row in rows])


@acceptance.get('/acceptance')
@login_required
def list_batches():
    with closing(connect()) as db:
        rows = db.execute('SELECT * FROM acceptance_batches ORDER BY id DESC').fetchall()
        return jsonify([serialize_batch(db, row) for row in rows])


@acceptance.post('/acceptance')
@roles_required('admin','manager','engineer')
def create_batch():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get('project'), str) or not payload['project'].strip():
        return jsonify(message='Công trình không hợp lệ.'), 400
    try:
        batch_date = date.fromisoformat(payload['batch_date']).isoformat()
    except (ValueError, TypeError, KeyError):
        return jsonify(message='Ngày nghiệm thu không hợp lệ.'), 400
    lines = payload.get('lines')
    if not isinstance(lines, list) or not lines or len(lines) > 100:
        return jsonify(message='Phiếu phải có từ 1 đến 100 hạng mục.'), 400
    try:
        with closing(connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            prepared = []
            for line in lines:
                if not isinstance(line, dict) or type(line.get('task_id')) is not int:
                    raise ValueError('Hạng mục không hợp lệ.')
                task = db.execute('SELECT cong_trinh FROM cong_viec WHERE id=?', (line['task_id'],)).fetchone()
                if not task or task['cong_trinh'] != payload['project']:
                    raise ValueError('Hạng mục không thuộc công trình.')
                if any(x[0] == line['task_id'] for x in prepared):
                    raise ValueError('Hạng mục bị trùng trong phiếu.')
                cumulative = decimal_number(line.get('cumulative'))
                previous = previous_approved(db, payload['project'], line['task_id'])
                if cumulative < previous:
                    raise ValueError('Lũy kế mới không được nhỏ hơn lũy kế đã duyệt.')
                prepared.append((line['task_id'], str(cumulative), str(cumulative - previous)))
            cursor = db.execute('INSERT INTO acceptance_batches(project,batch_date,created_by) VALUES (?,?,?)',
                                (payload['project'], batch_date, request.current_user['id']))
            db.executemany('INSERT INTO acceptance_lines(batch_id,task_id,cumulative,quantity) VALUES (?,?,?,?)',
                           [(cursor.lastrowid,*line) for line in prepared])
            db.commit()
            batch = db.execute('SELECT * FROM acceptance_batches WHERE id=?', (cursor.lastrowid,)).fetchone()
            return jsonify(serialize_batch(db, batch)), 201
    except ValueError as error:
        return jsonify(message=str(error)), 400


@acceptance.post('/acceptance/<int:batch_id>/approve')
@roles_required('admin','manager')
def approve_batch(batch_id):
    with closing(connect()) as db:
        db.execute('BEGIN IMMEDIATE')
        batch = db.execute('SELECT * FROM acceptance_batches WHERE id=?', (batch_id,)).fetchone()
        if not batch:
            return jsonify(message='Không tìm thấy phiếu.'), 404
        if batch['status'] == 'approved':
            return jsonify(serialize_batch(db,batch))
        lines = db.execute('SELECT * FROM acceptance_lines WHERE batch_id=?', (batch_id,)).fetchall()
        for line in lines:
            previous = previous_approved(db,batch['project'],line['task_id'],batch_id)
            if Decimal(line['cumulative']) < previous or Decimal(line['quantity']) != Decimal(line['cumulative'])-previous:
                return jsonify(message='Khối lượng lũy kế đã thay đổi; cần lập phiếu mới.'), 409
        db.execute("UPDATE acceptance_batches SET status='approved' WHERE id=?",(batch_id,))
        db.commit()
        return jsonify(serialize_batch(db,db.execute('SELECT * FROM acceptance_batches WHERE id=?',(batch_id,)).fetchone()))


@acceptance.post('/acceptance/<int:batch_id>/images')
@roles_required('admin','manager','engineer')
def upload_image(batch_id):
    with closing(connect()) as db:
        row = db.execute('SELECT status FROM acceptance_batches WHERE id=?',(batch_id,)).fetchone()
        if not row:
            return jsonify(message='Không tìm thấy phiếu.'),404
        if row['status'] != 'draft':
            return jsonify(message='Phiếu đã duyệt không thể sửa.'),409
        file = request.files.get('image')
        if file is None:
            return jsonify(message='Thiếu ảnh.'),400
        content = file.read(1024*1024+1)
        if len(content)>1024*1024 or not (content.startswith(b'\xff\xd8\xff') or content.startswith(b'\x89PNG\r\n\x1a\n')):
            return jsonify(message='Chỉ nhận JPEG/PNG tối đa 1 MB.'),400
        suffix = '.jpg' if content.startswith(b'\xff\xd8\xff') else '.png'
        filename = f'{uuid.uuid4().hex}{suffix}'
        folder = Path(current_app.config['USER_DATABASE']).parent/'acceptance_images'
        folder.mkdir(parents=True,exist_ok=True)
        target=folder/filename
        target.write_bytes(content)
        try:
            cur=db.execute('INSERT INTO acceptance_images(batch_id,filename,original_name) VALUES (?,?,?)',
                           (batch_id,filename,(file.filename or 'image')[:200]))
            db.commit()
        except Exception:
            target.unlink(missing_ok=True)
            raise
        return jsonify(id=cur.lastrowid,original_name=file.filename),201


@acceptance.get('/acceptance/images/<int:image_id>')
@login_required
def get_image(image_id):
    with closing(connect()) as db:
        row=db.execute('SELECT filename FROM acceptance_images WHERE id=?',(image_id,)).fetchone()
    if not row:
        return jsonify(message='Không tìm thấy ảnh.'),404
    return send_from_directory(Path(current_app.config['USER_DATABASE']).parent/'acceptance_images',row['filename'])
