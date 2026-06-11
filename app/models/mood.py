from datetime import datetime, timezone
from app.extensions import db

class MoodTracker(db.Model):
    __tablename__ = 'mood_tracker'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    mood = db.Column(db.String(20), nullable=False)
    mood_emoji = db.Column(db.String(10), nullable=False)
    note = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    employee = db.relationship('Employee', backref='moods')

    MOODS = {
        'excellent': {'emoji': '🤩', 'label': 'Excellent', 'color': '#48bb78'},
        'happy':     {'emoji': '😊', 'label': 'Happy',     'color': '#667eea'},
        'neutral':   {'emoji': '😐', 'label': 'Neutral',   'color': '#f6ad55'},
        'sad':       {'emoji': '😔', 'label': 'Sad',       'color': '#fc8181'},
        'stressed':  {'emoji': '😰', 'label': 'Stressed',  'color': '#e53e3e'},
    }

    def __repr__(self):
        return f'<Mood {self.employee_id} {self.mood} {self.date}>'