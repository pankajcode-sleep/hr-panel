from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from datetime import date, datetime
from app.extensions import db
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave import LeaveBalance, LeaveApplication, CompOff
from app.services.leave_service import apply_leave, get_or_create_balance, cancel_leave
from app.services.document_service import generate_payslip
import calendar
from sqlalchemy import extract
import os

self_service_bp = Blueprint('self_service', __name__)


def get_current_employee():
    return Employee.query.filter_by(user_id=current_user.id).first()


@self_service_bp.route('/my-portal')
@login_required
def portal():
    employee = get_current_employee()
    if not employee:
        flash('Account not linked to employee! Contact HR.', 'warning')
        return redirect(url_for('dashboard.index'))

    today = date.today()
    today_att = Attendance.query.filter_by(
        employee_id=employee.id, date=today
    ).first()
    balance = get_or_create_balance(employee.id)
    recent_leaves = LeaveApplication.query.filter_by(
        employee_id=employee.id
    ).order_by(LeaveApplication.applied_on.desc()).limit(5).all()

    month = today.month
    year = today.year
    month_records = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        extract('month', Attendance.date) == month,
        extract('year', Attendance.date) == year
    ).all()

    att_summary = {
        'present': len([r for r in month_records if r.status == 'Present']),
        'absent': len([r for r in month_records if r.status == 'Absent']),
        'late': len([r for r in month_records if r.status == 'Late']),
        'wfh': len([r for r in month_records if r.status == 'WFH']),
    }

    return render_template('self_service/portal.html',
                           employee=employee,
                           today_att=today_att,
                           balance=balance,
                           recent_leaves=recent_leaves,
                           att_summary=att_summary,
                           today=today,
                           month_name=calendar.month_name[month])


@self_service_bp.route('/my-profile')
@login_required
def my_profile():
    employee = get_current_employee()
    if not employee:
        flash('Account not linked!', 'warning')
        return redirect(url_for('dashboard.index'))
    return render_template('self_service/my_profile.html', employee=employee)


@self_service_bp.route('/my-profile/edit', methods=['GET', 'POST'])
@login_required
def edit_my_profile():
    employee = get_current_employee()
    if not employee:
        flash('Account not linked!', 'warning')
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        employee.phone = request.form.get('phone')
        employee.address = request.form.get('address')
        employee.emergency_contact = request.form.get('emergency_contact')
        photo = request.files.get('photo')
        if photo and photo.filename:
            UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'photos')
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            ALLOWED = {'png', 'jpg', 'jpeg'}
            if '.' in photo.filename and photo.filename.rsplit('.', 1)[1].lower() in ALLOWED:
                ext = photo.filename.rsplit('.', 1)[1].lower()
                import time
                filename = f'emp_{employee.employee_id}_{int(time.time())}.{ext}'
                if employee.photo:
                    old = os.path.join(UPLOAD_FOLDER, employee.photo)
                    if os.path.exists(old):
                        os.remove(old)
                photo.save(os.path.join(UPLOAD_FOLDER, filename))
                employee.photo = filename
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('self_service.my_profile'))
    return render_template('self_service/edit_my_profile.html', employee=employee)


@self_service_bp.route('/my-salary')
@login_required
def my_salary():
    employee = get_current_employee()
    if not employee:
        flash('Account not linked!', 'warning')
        return redirect(url_for('dashboard.index'))
    return render_template('self_service/my_salary.html',
                           employee=employee,
                           today=date.today())


@self_service_bp.route('/my-salary/download', methods=['POST'])
@login_required
def download_payslip():
    employee = get_current_employee()
    if not employee:
        return redirect(url_for('dashboard.index'))
    if not employee.salary:
        flash('Salary not set! Contact HR.', 'danger')
        return redirect(url_for('self_service.my_salary'))
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))
    buffer = generate_payslip(employee, month, year)
    return send_file(buffer, mimetype='application/pdf',
                     as_attachment=True,
                     download_name=f'payslip_{employee.employee_id}_{month}_{year}.pdf')


@self_service_bp.route('/my-attendance')
@login_required
def my_attendance():
    employee = get_current_employee()
    if not employee:
        flash('Account not linked!', 'warning')
        return redirect(url_for('dashboard.index'))

    month = request.args.get('month', date.today().month, type=int)
    year = request.args.get('year', date.today().year, type=int)
    _, days_in_month = calendar.monthrange(year, month)

    records = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        extract('month', Attendance.date) == month,
        extract('year', Attendance.date) == year
    ).order_by(Attendance.date).all()

    records_dict = {rec.date: rec for rec in records}
    all_dates = []
    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        rec = records_dict.get(d)
        all_dates.append({
            'date': d, 'record': rec,
            'is_sunday': d.weekday() == 6,
            'is_today': d == date.today(),
            'is_future': d > date.today()
        })

    summary = {
        'present': len([r for r in records if r.status == 'Present']),
        'absent': len([r for r in records if r.status == 'Absent']),
        'late': len([r for r in records if r.status == 'Late']),
        'half_day': len([r for r in records if r.status == 'Half Day']),
        'wfh': len([r for r in records if r.status == 'WFH']),
        'total_late_min': sum(r.late_minutes or 0 for r in records),
    }

    return render_template('self_service/my_attendance.html',
                           employee=employee,
                           all_dates=all_dates,
                           summary=summary,
                           month=month, year=year,
                           month_name=calendar.month_name[month])


@self_service_bp.route('/my-leaves')
@login_required
def my_leaves():
    employee = get_current_employee()
    if not employee:
        flash('Account not linked!', 'warning')
        return redirect(url_for('dashboard.index'))
    balance = get_or_create_balance(employee.id)
    leaves = LeaveApplication.query.filter_by(
        employee_id=employee.id
    ).order_by(LeaveApplication.applied_on.desc()).all()
    comp_offs = CompOff.query.filter_by(
        employee_id=employee.id
    ).order_by(CompOff.created_at.desc()).all()
    return render_template('self_service/my_leaves.html',
                           employee=employee,
                           balance=balance,
                           leaves=leaves,
                           comp_offs=comp_offs)


@self_service_bp.route('/apply-leave', methods=['GET', 'POST'])
@login_required
def apply_leave_self():
    employee = get_current_employee()
    if not employee:
        flash('Account not linked!', 'warning')
        return redirect(url_for('dashboard.index'))
    balance = get_or_create_balance(employee.id)
    if request.method == 'POST':
        leave_type = request.form.get('leave_type')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        reason = request.form.get('reason')
        if not all([leave_type, from_date, to_date]):
            flash('Please fill all required fields!', 'danger')
            return redirect(url_for('self_service.apply_leave_self'))
        from_d = date.fromisoformat(from_date)
        to_d = date.fromisoformat(to_date)
        if from_d > to_d:
            flash('From date cannot be after To date!', 'danger')
            return redirect(url_for('self_service.apply_leave_self'))
        success, message, application = apply_leave(
            employee.id, leave_type, from_date, to_date, reason
        )
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('self_service.my_leaves'))
    return render_template('self_service/apply_leave.html',
                           employee=employee,
                           balance=balance,
                           today=date.today())


@self_service_bp.route('/cancel-leave/<int:id>', methods=['POST'])
@login_required
def cancel_leave_self(id):
    employee = get_current_employee()
    if not employee:
        return redirect(url_for('dashboard.index'))
    success, message = cancel_leave(id, employee.id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('self_service.my_leaves'))


@self_service_bp.route('/request-comp-off', methods=['GET', 'POST'])
@login_required
def request_comp_off():
    employee = get_current_employee()
    if not employee:
        flash('Account not linked!', 'warning')
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        work_date = request.form.get('work_date')
        reason = request.form.get('reason')
        work_type = request.form.get('work_type')
        if not work_date or not reason:
            flash('Please fill all fields!', 'danger')
            return redirect(url_for('self_service.request_comp_off'))
        work_d = date.fromisoformat(work_date)
        is_sunday = work_d.weekday() == 6
        comp = CompOff(
            employee_id=employee.id,
            work_date=work_d,
            reason=f"[{work_type}] {reason}" + (" [SUNDAY]" if is_sunday else ""),
            status='Pending'
        )
        db.session.add(comp)
        db.session.commit()
        flash('Comp Off request submitted!', 'success')
        return redirect(url_for('self_service.my_leaves'))
    return render_template('self_service/request_comp_off.html', employee=employee)