from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timezone, date
from app.extensions import db
from app.models.leave import LeaveApplication, CompOff
from app.models.employee import Employee
from app.services.leave_service import (
    approve_leave, reject_leave, get_or_create_balance
)
from app.utils.decorators import hr_required

leave_bp = Blueprint('leave', __name__)


@leave_bp.route('/manage')
@hr_required
def manage():
    status_filter = request.args.get('status', 'Pending')
    leaves = LeaveApplication.query.filter_by(
        status=status_filter
    ).order_by(LeaveApplication.applied_on.desc()).all()
    comp_offs = CompOff.query.filter_by(
        status='Pending'
    ).order_by(CompOff.created_at.desc()).all()
    return render_template('leave/manage.html',
                           leaves=leaves,
                           comp_offs=comp_offs,
                           status_filter=status_filter)


@leave_bp.route('/approve/<int:id>', methods=['POST'])
@hr_required
def approve(id):
    success, message = approve_leave(id, current_user.id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('leave.manage'))


@leave_bp.route('/reject/<int:id>', methods=['POST'])
@hr_required
def reject(id):
    reject_reason = request.form.get('reject_reason', 'Not specified')
    success, message = reject_leave(id, current_user.id, reject_reason)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('leave.manage'))


@leave_bp.route('/comp-off/approve/<int:id>', methods=['POST'])
@hr_required
def approve_comp_off(id):
    comp = CompOff.query.get_or_404(id)
    comp.status = 'Approved'
    comp.approved_by = current_user.id
    comp.approved_on = datetime.now(timezone.utc)
    balance = get_or_create_balance(comp.employee_id)
    balance.comp_off = float(balance.comp_off) + 1.0
    db.session.commit()
    flash('Comp Off approved! +1 added.', 'success')
    return redirect(url_for('leave.manage'))


@leave_bp.route('/comp-off/reject/<int:id>', methods=['POST'])
@hr_required
def reject_comp_off(id):
    comp = CompOff.query.get_or_404(id)
    comp.status = 'Rejected'
    comp.approved_by = current_user.id
    comp.approved_on = datetime.now(timezone.utc)
    db.session.commit()
    flash('Comp Off rejected.', 'info')
    return redirect(url_for('leave.manage'))


@leave_bp.route('/report')
@hr_required
def report():
    employees = Employee.query.filter_by(status='Active').all()
    year = date.today().year
    report_data = []
    for emp in employees:
        balance = get_or_create_balance(emp.id, year)
        total_leaves = LeaveApplication.query.filter_by(
            employee_id=emp.id, status='Approved'
        ).count()
        report_data.append({
            'employee': emp,
            'balance': balance,
            'total_approved': total_leaves
        })
    return render_template('leave/report.html',
                           report_data=report_data, year=year)