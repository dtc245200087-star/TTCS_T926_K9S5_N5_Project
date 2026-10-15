from app.extensions import db
from datetime import datetime

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    leader_id = db.Column(db.Integer, nullable=True) # ID Đội trưởng

class CongViec(db.Model):
    __tablename__ = 'cong_viec'
    id = db.Column(db.Integer, primary_key=True)
    ten_cong_viec = db.Column(db.String(200), nullable=False)
    tu_ngay = db.Column(db.DateTime, nullable=False)
    den_ngay = db.Column(db.DateTime, nullable=False)
    doi_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)

    @property
    def title(self):
        return self.ten_cong_viec

    @property
    def start_date(self):
        return self.tu_ngay

    @property
    def end_date(self):
        return self.den_ngay

    @property
    def team_id(self):
        return self.doi_id

    @team_id.setter
    def team_id(self, value):
        self.doi_id = value

Task = CongViec

class TaskHistory(db.Model):
    __tablename__ = 'task_history'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('cong_viec.id'), nullable=False)
    old_team_id = db.Column(db.Integer, nullable=True)
    new_team_id = db.Column(db.Integer, nullable=False)
    changed_by_user_id = db.Column(db.Integer, nullable=True) # ID Chỉ huy trưởng
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)