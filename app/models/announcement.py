from datetime import datetime, timezone, date
from app.extensions import db

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')
    priority = db.Column(db.String(10), default='normal')
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expires_on = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    creator = db.relationship('User', backref='announcements')

    TYPES = {
        'info':    {'icon': 'ℹ️', 'color': '#667eea', 'bg': '#ebf4ff', 'label': 'Info'},
        'warning': {'icon': '⚠️', 'color': '#f6ad55', 'bg': '#fffaf0', 'label': 'Warning'},
        'success': {'icon': '✅', 'color': '#48bb78', 'bg': '#f0fff4', 'label': 'Success'},
        'danger':  {'icon': '🚨', 'color': '#fc8181', 'bg': '#fff5f5', 'label': 'Urgent'},
        'holiday': {'icon': '🎉', 'color': '#b794f4', 'bg': '#faf5ff', 'label': 'Holiday'},
        'event':   {'icon': '📅', 'color': '#63b3ed', 'bg': '#ebf8ff', 'label': 'Event'},
    }

    PRIORITIES = {
        'normal': {'label': 'Normal', 'color': '#718096'},
        'high':   {'label': 'High',   'color': '#f6ad55'},
        'urgent': {'label': 'Urgent', 'color': '#fc8181'},
    }

    @property
    def is_expired(self):
        if self.expires_on:
            return date.today() > self.expires_on
        return False

    @property
    def type_data(self):
        return self.TYPES.get(self.type, self.TYPES['info'])

    @property
    def priority_data(self):
        return self.PRIORITIES.get(self.priority, self.PRIORITIES['normal'])

    def __repr__(self):
        return f'<Announcement {self.title}>'