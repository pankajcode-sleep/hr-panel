from datetime import datetime, timezone
from app.extensions import db

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    photo = db.Column(db.String(255))
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    date_joined = db.Column(db.Date)
    employment_type = db.Column(db.String(20), default='Full-time')
    salary = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20), default='Active')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    blood_group = db.Column(db.String(5), nullable=True)
    marital_status = db.Column(db.String(20), nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    religion = db.Column(db.String(50), nullable=True)
    emergency_contact = db.Column(db.String(20), nullable=True)
    user_account = db.relationship('User', backref=db.backref('employee', uselist=False))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_active(self):
        return self.status == 'Active'

    def __repr__(self):
        return f'<Employee {self.full_name}>'