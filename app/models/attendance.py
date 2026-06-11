from datetime import datetime, timezone, time
from app.extensions import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Present')
    check_in = db.Column(db.Time, nullable=True)
    check_out = db.Column(db.Time, nullable=True)
    late_minutes = db.Column(db.Integer, default=0)
    note = db.Column(db.Text, nullable=True)
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    punch_in_lat = db.Column(db.Numeric(10, 8), nullable=True)
    punch_in_lng = db.Column(db.Numeric(11, 8), nullable=True)
    punch_in_photo = db.Column(db.String(255), nullable=True)
    punch_in_address = db.Column(db.Text, nullable=True)
    punch_out_lat = db.Column(db.Numeric(10, 8), nullable=True)
    punch_out_lng = db.Column(db.Numeric(11, 8), nullable=True)
    punch_out_photo = db.Column(db.String(255), nullable=True)
    punch_out_address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    employee = db.relationship('Employee', backref='attendance_records')
    marker = db.relationship('User', backref='marked_attendance')

    OFFICE_TIME = time(9, 0, 0)
    LATE_THRESHOLD = 15

    @property
    def is_late(self):
        return self.late_minutes > self.LATE_THRESHOLD if self.late_minutes else False

    @property
    def working_hours(self):
        if self.check_in and self.check_out:
            from datetime import datetime, date
            dt_in = datetime.combine(date.today(), self.check_in)
            dt_out = datetime.combine(date.today(), self.check_out)
            diff = dt_out - dt_in
            return round(diff.seconds / 3600, 2)
        return 0

    @staticmethod
    def calculate_late_minutes(check_in_time):
        if not check_in_time:
            return 0
        from datetime import datetime, date
        office = datetime.combine(date.today(), Attendance.OFFICE_TIME)
        actual = datetime.combine(date.today(), check_in_time)
        diff = (actual - office).seconds // 60
        return diff if actual > office else 0

    def __repr__(self):
        return f'<Attendance {self.employee_id} {self.date} {self.status}>'