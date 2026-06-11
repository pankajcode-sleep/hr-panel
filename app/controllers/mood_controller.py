from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import date, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models.mood import MoodTracker
from app.models.employee import Employee
from app.utils.decorators import hr_required

mood_bp = Blueprint('mood', __name__)


@mood_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        flash('Account not linked to employee!', 'warning')
        return redirect(url_for('dashboard.index'))

    today = date.today()
    today_mood = MoodTracker.query.filter_by(
        employee_id=employee.id, date=today
    ).first()

    if request.method == 'POST':
        mood_key = request.form.get('mood')
        note = request.form.get('note', '')
        if mood_key not in MoodTracker.MOODS:
            flash('Invalid mood!', 'danger')
            return redirect(url_for('mood.submit'))
        mood_data = MoodTracker.MOODS[mood_key]
        if today_mood:
            today_mood.mood = mood_key
            today_mood.mood_emoji = mood_data['emoji']
            today_mood.note = note
        else:
            new_mood = MoodTracker(
                employee_id=employee.id,
                mood=mood_key,
                mood_emoji=mood_data['emoji'],
                note=note,
                date=today
            )
            db.session.add(new_mood)
        db.session.commit()
        flash('Mood submitted!', 'success')
        return redirect(url_for('self_service.portal'))

    return render_template('mood/submit.html',
                           employee=employee,
                           today_mood=today_mood,
                           moods=MoodTracker.MOODS,
                           today=today)


@mood_bp.route('/team')
@hr_required
def team_mood():
    today = date.today()
    week_ago = today - timedelta(days=7)

    today_moods = db.session.query(MoodTracker, Employee).join(
        Employee, MoodTracker.employee_id == Employee.id
    ).filter(MoodTracker.date == today).all()

    mood_counts = {}
    for mood_key in MoodTracker.MOODS:
        count = MoodTracker.query.filter_by(date=today, mood=mood_key).count()
        mood_counts[mood_key] = count

    daily_trend = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_moods = MoodTracker.query.filter_by(date=d).all()
        if day_moods:
            avg = {'excellent': 5, 'happy': 4, 'neutral': 3, 'sad': 2, 'stressed': 1}
            scores = [avg.get(m.mood, 3) for m in day_moods]
            avg_score = sum(scores) / len(scores)
        else:
            avg_score = 0
        daily_trend.append({
            'date': d.strftime('%d %b'),
            'score': round(avg_score, 1),
            'count': len(day_moods)
        })

    all_employees = Employee.query.filter_by(status='Active').all()
    submitted_ids = [m.employee_id for m, e in today_moods]
    not_submitted = [e for e in all_employees if e.id not in submitted_ids]

    return render_template('mood/team.html',
                           today_moods=today_moods,
                           mood_counts=mood_counts,
                           daily_trend=daily_trend,
                           not_submitted=not_submitted,
                           moods=MoodTracker.MOODS,
                           today=today)


@mood_bp.route('/history')
@login_required
def history():
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        flash('Account not linked!', 'warning')
        return redirect(url_for('dashboard.index'))
    moods = MoodTracker.query.filter_by(
        employee_id=employee.id
    ).order_by(MoodTracker.date.desc()).limit(30).all()
    return render_template('mood/history.html',
                           employee=employee,
                           moods=moods,
                           mood_data=MoodTracker.MOODS)