from datetime import date, timedelta
from heapq import heapify, heappop, heappush
from math import ceil

from ..models.cong_viec import CongViec
from ..models.lich_lam_viec import CongViecPhuThuoc


def _working_day(value, weekdays, holidays):
    return value.weekday() in weekdays and value not in holidays


def _next_workday(value, weekdays, holidays):
    while not _working_day(value, weekdays, holidays):
        value += timedelta(days=1)
    return value


def _add_workdays(start, duration, weekdays, holidays):
    current = _next_workday(start, weekdays, holidays)
    for _ in range(max(1, duration) - 1):
        current += timedelta(days=1)
        current = _next_workday(current, weekdays, holidays)
    return current


def _workdays_between(start, finish, weekdays, holidays):
    if start == finish:
        return 0
    if finish < start:
        return -_workdays_between(finish, start, weekdays, holidays)
    days = 0
    current = start
    while current < finish:
        current += timedelta(days=1)
        if _working_day(current, weekdays, holidays):
            days += 1
    return days


def _ordered_tasks(tasks, predecessors):
    by_id = {task.id: task for task in tasks}
    dependencies = {task.id: set(predecessors.get(task.id, ())) & by_id.keys() for task in tasks}
    successors = {task.id: [] for task in tasks}
    for task_id, predecessor_ids in dependencies.items():
        for predecessor_id in predecessor_ids:
            successors[predecessor_id].append(task_id)
    pending = {task_id: len(predecessor_ids) for task_id, predecessor_ids in dependencies.items()}
    ready = [task_id for task_id, count in pending.items() if count == 0]
    heapify(ready)
    ordered = []
    while ready:
        task_id = heappop(ready)
        ordered.append(by_id[task_id])
        for successor_id in successors[task_id]:
            pending[successor_id] -= 1
            if pending[successor_id] == 0:
                heappush(ready, successor_id)
    if len(ordered) != len(tasks):
        raise ValueError("Mạng công việc có chu trình phụ thuộc.")
    return ordered


def du_bao_cong_trinh(project, calendar, today=None):
    today = today or date.today()
    tasks = CongViec.query.filter_by(cong_trinh_id=project.id).order_by(CongViec.id).all()
    task_ids = [task.id for task in tasks]
    dependencies = {task_id: [] for task_id in task_ids}
    for relation in CongViecPhuThuoc.query.filter(CongViecPhuThuoc.cong_viec_id.in_(task_ids)).all() if task_ids else []:
        dependencies[relation.cong_viec_id].append(relation.tien_quyet_id)
    ordered = _ordered_tasks(tasks, dependencies)
    weekdays = set(calendar.ngay_lam_viec)
    holidays = {item.ngay for item in calendar.ngay_nghi}
    project_start = project.ngay_bat_dau or today

    def calculate(use_actuals):
        schedule = {}
        for task in ordered:
            predecessors = [schedule[item] for item in dependencies[task.id] if item in schedule]
            earliest = max((item["finish"] for item in predecessors), default=project_start - timedelta(days=1))
            earliest = _next_workday(earliest + timedelta(days=1), weekdays, holidays)
            if use_actuals and task.ngay_hoan_thanh_thuc_te:
                start = _next_workday(task.ngay_bat_dau_thuc_te or earliest, weekdays, holidays)
                finish = task.ngay_hoan_thanh_thuc_te
                remaining = 0
            elif use_actuals and (task.ngay_bat_dau_thuc_te or task.tien_do > 0 or task.trang_thai == "Đang thực hiện"):
                start = _next_workday(max(earliest, task.ngay_bat_dau_thuc_te or today, today), weekdays, holidays)
                remaining = max(1, ceil(task.thoi_luong_ngay * (100 - task.tien_do) / 100))
                finish = _add_workdays(start, remaining, weekdays, holidays)
            else:
                start = earliest
                remaining = max(1, task.thoi_luong_ngay)
                finish = _add_workdays(start, remaining, weekdays, holidays)
            schedule[task.id] = {"start": start, "finish": finish, "remaining": remaining}
        return schedule

    planned = calculate(False)
    current = calculate(True)
    planned_finish = project.ngay_ket_thuc_du_kien or max((item["finish"] for item in planned.values()), default=project_start)
    forecast_finish = max((item["finish"] for item in current.values()), default=project_start)
    critical = {task_id for task_id, item in current.items() if item["finish"] == forecast_finish}
    pending = list(critical)
    while pending:
        task_id = pending.pop()
        task_start = current[task_id]["start"]
        for predecessor_id in dependencies[task_id]:
            predecessor_finish = current[predecessor_id]["finish"]
            next_start = _next_workday(predecessor_finish + timedelta(days=1), weekdays, holidays)
            if next_start == task_start and predecessor_id not in critical:
                critical.add(predecessor_id)
                pending.append(predecessor_id)

    return {
        "cong_trinh_id": project.id,
        "ten_cong_trinh": project.ten_cong_trinh,
        "ngay_hoan_thanh_hien_tai": forecast_finish.isoformat(),
        "ngay_hoan_thanh_ke_hoach": planned_finish.isoformat(),
        "chenh_lech_ngay_lam_viec": _workdays_between(planned_finish, forecast_finish, weekdays, holidays),
        "cong_viec_gang": sorted(critical),
        "cong_viec": [
            {
                **task.to_dict(),
                "ngay_bat_dau_du_bao": current[task.id]["start"].isoformat(),
                "ngay_hoan_thanh_du_bao": current[task.id]["finish"].isoformat(),
                "con_lai_ngay_lam_viec": current[task.id]["remaining"],
                "phu_thuoc": dependencies[task.id],
                "la_cong_viec_gang": task.id in critical,
            }
            for task in tasks
        ],
    }
