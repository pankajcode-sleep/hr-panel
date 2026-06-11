from datetime import datetime, timezone
from app.extensions import db

class LeaveBalance(db.Model):
    __tablename__ = 'leave_balance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    year = db.Column(db.Integer, default=2025)
    casual_leave = db.Column(db.Numeric(4, 1), default=12.0)
    sick_leave = db.Column(db.Numeric(4, 1), default=12.0)
    earned_leave = db.Column(db.Numeric(4, 1), default=15.0)
    comp_off = db.Column(db.Numeric(4, 1), default=0.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    employee = db.relationship('Employee', backref='leave_balance')

    def get_balance(self, leave_type):
        mapping = {
            'CL': self.casual_leave,
            'SL': self.sick_leave,
            'EL': self.earned_leave,
            'Comp Off': self.comp_off,
        }
        return float(mapping.get(leave_type, 0))

    def deduct(self, leave_type, days):
        if leave_type == 'CL':
            self.casual_leave = float(self.casual_leave) - days
        elif leave_type == 'SL':
            self.sick_leave = float(self.sick_leave) - days
        elif leave_type == 'EL':
            self.earned_leave = float(self.earned_leave) - days
        elif leave_type == 'Comp Off':
            self.comp_off = float(self.comp_off) - days

    def add_back(self, leave_type, days):
        if leave_type == 'CL':
            self.casual_leave = float(self.casual_leave) + days
        elif leave_type == 'SL':
            self.sick_leave = float(self.sick_leave) + days
        elif leave_type == 'EL':
            self.earned_leave = float(self.earned_leave) + days
        elif leave_type == 'Comp Off':
            self.comp_off = float(self.comp_off) + days

    def __repr__(self):
        return f'<LeaveBalance {self.employee_id} {self.year}>'


class LeaveApplication(db.Model):
    __tablename__ = 'leave_application'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type = db.Column(db.String(20), nullable=False)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Numeric(4, 1), nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    applied_on = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_on = db.Column(db.DateTime, nullable=True)
    reject_reason = db.Column(db.Text, nullable=True)
    employee = db.relationship('Employee', backref='leave_applications')
    reviewer = db.relationship('User', backref='reviewed_leaves')

    def __repr__(self):
        return f'<Leave {self.employee_id} {self.leave_type} {self.status}>'


class CompOff(db.Model):
    __tablename__ = 'comp_off'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_on = db.Column(db.DateTime, nullable=True)
    used_on = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    employee = db.relationship('Employee', backref='comp_offs')
    approver = db.relationship('User', backref='approved_comp_offs')

    def __repr__(self):
        return f'<CompOff {self.employee_id} {self.work_date}>'