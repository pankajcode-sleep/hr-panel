from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import date
from app.extensions import db
from app.models.announcement import Announcement
from app.utils.decorators import hr_required

announcement_bp = Blueprint('announcement', __name__)


@announcement_bp.route('/')
@login_required
def index():
    announcements = Announcement.query.filter_by(
        is_active=True
    ).order_by(
        Announcement.priority.desc(),
        Announcement.created_at.desc()
    ).all()
    active = [a for a in announcements if not a.is_expired]
    urgent = [a for a in active if a.priority == 'urgent']
    normal = [a for a in active if a.priority != 'urgent']
    return render_template('announcement/index.html',
                           urgent=urgent, normal=normal)


@announcement_bp.route('/create', methods=['GET', 'POST'])
@hr_required
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        ann_type = request.form.get('type', 'info')
        priority = request.form.get('priority', 'normal')
        expires_on = request.form.get('expires_on') or None
        if not title or not content:
            flash('Title and content required!', 'danger')
            return redirect(url_for('announcement.create'))
        ann = Announcement(
            title=title, content=content, type=ann_type,
            priority=priority, expires_on=expires_on,
            created_by=current_user.id, is_active=True
        )
        db.session.add(ann)
        db.session.commit()
        flash(f'Announcement published!', 'success')
        return redirect(url_for('announcement.manage'))
    return render_template('announcement/create.html',
                           types=Announcement.TYPES,
                           priorities=Announcement.PRIORITIES)


@announcement_bp.route('/manage')
@hr_required
def manage():
    announcements = Announcement.query.order_by(
        Announcement.created_at.desc()
    ).all()
    return render_template('announcement/manage.html',
                           announcements=announcements,
                           types=Announcement.TYPES,
                           priorities=Announcement.PRIORITIES)


@announcement_bp.route('/<int:id>/toggle', methods=['POST'])
@hr_required
def toggle(id):
    ann = Announcement.query.get_or_404(id)
    ann.is_active = not ann.is_active
    db.session.commit()
    flash('Announcement updated!', 'success')
    return redirect(url_for('announcement.manage'))


@announcement_bp.route('/<int:id>/delete', methods=['POST'])
@hr_required
def delete(id):
    ann = Announcement.query.get_or_404(id)
    db.session.delete(ann)
    db.session.commit()
    flash('Announcement deleted!', 'success')
    return redirect(url_for('announcement.manage'))


@announcement_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@hr_required
def edit(id):
    ann = Announcement.query.get_or_404(id)
    if request.method == 'POST':
        ann.title = request.form.get('title', '').strip()
        ann.content = request.form.get('content', '').strip()
        ann.type = request.form.get('type', 'info')
        ann.priority = request.form.get('priority', 'normal')
        ann.expires_on = request.form.get('expires_on') or None
        db.session.commit()
        flash('Announcement updated!', 'success')
        return redirect(url_for('announcement.manage'))
    return render_template('announcement/edit.html',
                           ann=ann,
                           types=Announcement.TYPES,
                           priorities=Announcement.PRIORITIES)


@announcement_bp.route('/latest')
@login_required
def latest():
    announcements = Announcement.query.filter_by(
        is_active=True
    ).order_by(Announcement.created_at.desc()).limit(5).all()
    active = [a for a in announcements if not a.is_expired]
    data = [{
        'id': a.id,
        'title': a.title,
        'type': a.type,
        'icon': a.type_data['icon'],
        'color': a.type_data['color'],
        'priority': a.priority,
        'created_at': a.created_at.strftime('%d %b %Y')
    } for a in active]
    return jsonify(data)