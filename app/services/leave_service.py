from datetime import date, timedelta
from app.models.leave import LeaveBalance, LeaveApplication
from app.extensions import db


def calculate_leave_days(from_date, to_date, apply_sandwich=True):
    if isinstance(from_date, str):
        from_date = date.fromisoformat(from_date)
    if isinstance(to_date, str):
        to_date = date.fromisoformat(to_date)

    total_days = (to_date - from_date).days + 1

    if not apply_sandwich:
        return total_days

    day_before = from_date - timedelta(days=1)
    day_after = to_date + timedelta(days=1)
    extra_days = 0

    if day_before.weekday() == 6:
        saturday = day_before - timedelta(days=1)
        if saturday.weekday() == 5:
            extra_days += 2

    if day_after.weekday() == 0:
        sunday = day_after - timedelta(days=1)
        if sunday.weekday() == 6:
            if day_before.weekday() != 6:
                extra_days += 2

    return total_days + extra_days


def get_or_create_balance(employee_id, year=None):
    if year is None:
        year = date.today().year

    balance = LeaveBalance.query.filter_by(
        employee_id=employee_id,
        year=year
    ).first()

    if not balance:
        balance = LeaveBalance(
            employee_id=employee_id,
            year=year,
            casual_leave=12.0,
            sick_leave=12.0,
            earned_leave=15.0,
            comp_off=0.0
        )
        db.session.add(balance)
        db.session.commit()

    return balance


def check_balance(employee_id, leave_type, days):
    if leave_type == 'LOP':
        return True, 999
    balance = get_or_create_balance(employee_id)
    available = balance.get_balance(leave_type)
    return available >= days, available


def apply_leave(employee_id, leave_type, from_date, to_date, reason):
    total_days = calculate_leave_days(from_date, to_date)

    if leave_type != 'LOP':
        has_balance, available = check_balance(employee_id, leave_type, total_days)
        if not has_balance:
            return False, f'Insufficient balance! Available: {available} days, Required: {total_days} days', None

    application = LeaveApplication(
        employee_id=employee_id,
        leave_type=leave_type,
        from_date=from_date,
        to_date=to_date,
        total_days=total_days,
        reason=reason,
        status='Pending'
    )
    db.session.add(application)
    db.session.commit()
    return True, f'Leave applied! Total days: {total_days}', application


def approve_leave(application_id, reviewer_id):
    from datetime import datetime, timezone
    application = LeaveApplication.query.get_or_404(application_id)

    if application.status != 'Pending':
        return False, 'Already processed!'

    if application.leave_type != 'LOP':
        balance = get_or_create_balance(application.employee_id)
        balance.deduct(application.leave_type, float(application.total_days))

    application.status = 'Approved'
    application.reviewed_by = reviewer_id
    application.reviewed_on = datetime.now(timezone.utc)
    db.session.commit()
    return True, 'Leave approved!'


def reject_leave(application_id, reviewer_id, reject_reason):
    from datetime import datetime, timezone
    application = LeaveApplication.query.get_or_404(application_id)

    if application.status != 'Pending':
        return False, 'Already processed!'

    application.status = 'Rejected'
    application.reviewed_by = reviewer_id
    application.reviewed_on = datetime.now(timezone.utc)
    application.reject_reason = reject_reason
    db.session.commit()
    return True, 'Leave rejected!'


def cancel_leave(application_id, employee_id):
    application = LeaveApplication.query.get_or_404(application_id)

    if application.employee_id != employee_id:
        return False, 'Unauthorized!'

    if application.status != 'Pending':
        return False, 'Only pending leaves can be cancelled!'

    application.status = 'Cancelled'
    db.session.commit()
    return True, 'Leave cancelled!'