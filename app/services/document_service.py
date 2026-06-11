from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import datetime, date


def generate_payslip(employee, month, year):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=1.5*cm, leftMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    elements = []
    dark_blue = colors.HexColor('#1a1a2e')
    light_gray = colors.HexColor('#f8f9fa')
    green = colors.HexColor('#1cc88a')
    white = colors.white
    month_name = datetime(year, month, 1).strftime('%B %Y')

    header_data = [[
        Paragraph('<font color="white" size="18"><b>HR PANEL</b></font>', styles['Normal']),
        Paragraph(f'<font color="white" size="10">SALARY SLIP<br/>{month_name}</font>', styles['Normal'])
    ]]
    header_table = Table(header_data, colWidths=[10*cm, 8*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), dark_blue),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*cm))

    emp_data = [
        ['Employee Details', ''],
        ['Name', employee.full_name],
        ['Employee ID', employee.employee_id],
        ['Department', employee.department or '-'],
        ['Designation', employee.designation or '-'],
        ['Employment Type', employee.employment_type or '-'],
    ]
    emp_table = Table(emp_data, colWidths=[9*cm, 9*cm])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), dark_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('SPAN', (0, 0), (-1, 0)),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, light_gray]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 0.5*cm))

    basic_salary = float(employee.salary or 0)
    hra = round(basic_salary * 0.40, 2)
    transport = round(basic_salary * 0.10, 2)
    medical = round(basic_salary * 0.05, 2)
    gross_salary = basic_salary + hra + transport + medical
    pf = round(basic_salary * 0.12, 2)
    tax = round(gross_salary * 0.05, 2)
    total_deductions = pf + tax
    net_salary = gross_salary - total_deductions

    earnings_data = [
        ['EARNINGS', 'AMOUNT (₹)', 'DEDUCTIONS', 'AMOUNT (₹)'],
        ['Basic Salary', f'{basic_salary:,.2f}', 'Provident Fund (12%)', f'{pf:,.2f}'],
        ['HRA (40%)', f'{hra:,.2f}', 'Income Tax (5%)', f'{tax:,.2f}'],
        ['Transport Allowance', f'{transport:,.2f}', '', ''],
        ['Medical Allowance', f'{medical:,.2f}', '', ''],
        ['', '', '', ''],
        ['Gross Salary', f'{gross_salary:,.2f}', 'Total Deductions', f'{total_deductions:,.2f}'],
    ]
    salary_table = Table(earnings_data, colWidths=[6*cm, 3*cm, 6*cm, 3*cm])
    salary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), dark_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [white, light_gray]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(salary_table)
    elements.append(Spacer(1, 0.5*cm))

    net_data = [[f'NET SALARY: Rs. {net_salary:,.2f}']]
    net_table = Table(net_data, colWidths=[18*cm])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), green),
        ('TEXTCOLOR', (0, 0), (-1, -1), white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(net_table)
    elements.append(Spacer(1, 1*cm))

    footer_data = [[
        'Generated on: ' + datetime.now().strftime('%d %B %Y'),
        'Authorized Signature: _______________'
    ]]
    footer_table = Table(footer_data, colWidths=[9*cm, 9*cm])
    footer_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dee2e6')))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(footer_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_offer_letter(employee):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    dark_blue = colors.HexColor('#1a1a2e')
    elements = []

    header_data = [[
        Paragraph('<font color="white" size="20"><b>HR PANEL</b></font>', styles['Normal']),
        Paragraph('<font color="white" size="10">OFFER LETTER</font>', styles['Normal'])
    ]]
    header_table = Table(header_data, colWidths=[10*cm, 7*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), dark_blue),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 1*cm))

    today = date.today().strftime('%d %B %Y')
    elements.append(Paragraph(f'Date: {today}', styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f'<b>To,</b>', styles['Normal']))
    elements.append(Paragraph(f'<b>{employee.full_name}</b>', styles['Normal']))
    elements.append(Paragraph(f'{employee.email}', styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    subject_style = ParagraphStyle('subject', fontSize=12,
                                    fontName='Helvetica-Bold', textColor=dark_blue)
    elements.append(Paragraph(
        f'Subject: Offer of Employment - {employee.designation or "Position"}',
        subject_style
    ))
    elements.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor('#dee2e6')))
    elements.append(Spacer(1, 0.5*cm))

    body_text = f"""
    Dear <b>{employee.first_name}</b>,<br/><br/>
    We are pleased to offer you the position of <b>{employee.designation or 'Employee'}</b>
    in the <b>{employee.department or 'General'}</b> department at <b>HR Panel Company</b>.<br/><br/>
    <b>Terms of Employment:</b>
    """
    elements.append(Paragraph(body_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*cm))

    terms_data = [
        ['Position', employee.designation or '-'],
        ['Department', employee.department or '-'],
        ['Employment Type', employee.employment_type or 'Full-time'],
        ['Date of Joining', str(employee.date_joined) if employee.date_joined else str(date.today())],
        ['Salary (Monthly)', f'Rs. {float(employee.salary):,.2f}' if employee.salary else 'As discussed'],
    ]
    terms_table = Table(terms_data, colWidths=[7*cm, 10*cm])
    terms_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(terms_table)
    elements.append(Spacer(1, 0.5*cm))

    closing_text = """
    This offer is contingent upon successful completion of background verification.<br/><br/>
    Please sign and return a copy of this letter as confirmation of your acceptance
    within <b>7 days</b> of receipt.<br/><br/>
    We look forward to welcoming you to our team!<br/><br/>
    Warm regards,<br/>
    <b>HR Department</b><br/>
    HR Panel Company
    """
    elements.append(Paragraph(closing_text, styles['Normal']))
    elements.append(Spacer(1, 1.5*cm))

    sig_data = [
        ['Authorized Signature', 'Candidate Acceptance'],
        ['', ''],
        ['___________________', '___________________'],
        ['HR Manager', employee.full_name],
        [today, '_________________ (Date)'],
    ]
    sig_table = Table(sig_data, colWidths=[9*cm, 9*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('TEXTCOLOR', (0, 0), (-1, 0), dark_blue),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_increment_letter(employee, old_salary, new_salary, effective_date):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    dark_blue = colors.HexColor('#1a1a2e')
    elements = []

    header_data = [[
        Paragraph('<font color="white" size="20"><b>HR PANEL</b></font>', styles['Normal']),
        Paragraph('<font color="white" size="10">INCREMENT LETTER</font>', styles['Normal'])
    ]]
    header_table = Table(header_data, colWidths=[10*cm, 7*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), dark_blue),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 1*cm))

    today = date.today().strftime('%d %B %Y')
    elements.append(Paragraph(f'Date: {today}', styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph('<b>To,</b>', styles['Normal']))
    elements.append(Paragraph(f'<b>{employee.full_name}</b>', styles['Normal']))
    elements.append(Paragraph(f'Employee ID: {employee.employee_id}', styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    subject_style = ParagraphStyle('subject', fontSize=12,
                                    fontName='Helvetica-Bold', textColor=dark_blue)
    elements.append(Paragraph('Subject: Salary Increment Letter', subject_style))
    elements.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor('#dee2e6')))
    elements.append(Spacer(1, 0.5*cm))

    increment_amount = float(new_salary) - float(old_salary)
    increment_percent = (increment_amount / float(old_salary)) * 100 if old_salary else 0

    body = f"""
    Dear <b>{employee.first_name}</b>,<br/><br/>
    We are pleased to inform you that based on your outstanding performance,
    the management has decided to revise your salary with effect from
    <b>{effective_date}</b>.<br/><br/>
    """
    elements.append(Paragraph(body, styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    salary_data = [
        ['Salary Details', 'Amount (Rs.)'],
        ['Previous Salary (Monthly)', f'Rs. {float(old_salary):,.2f}'],
        ['Increment Amount', f'Rs. {increment_amount:,.2f}'],
        ['Increment Percentage', f'{increment_percent:.1f}%'],
        ['New Salary (Monthly)', f'Rs. {float(new_salary):,.2f}'],
    ]
    salary_table = Table(salary_data, colWidths=[10*cm, 7*cm])
    salary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), dark_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(salary_table)
    elements.append(Spacer(1, 0.5*cm))

    closing = """
    We appreciate your continued efforts and look forward to your further
    growth with the organization.<br/><br/>
    Congratulations on this well-deserved increment!<br/><br/>
    Best regards,<br/>
    <b>HR Department</b><br/>
    HR Panel Company
    """
    elements.append(Paragraph(closing, styles['Normal']))
    elements.append(Spacer(1, 1.5*cm))

    sig_data = [
        ['Authorized Signature', 'Acknowledged by'],
        ['', ''],
        ['___________________', '___________________'],
        ['HR Manager', employee.full_name],
        [today, '_________________ (Date)'],
    ]
    sig_table = Table(sig_data, colWidths=[9*cm, 9*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), dark_blue),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer