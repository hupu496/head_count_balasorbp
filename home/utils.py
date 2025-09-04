import os
from django.template.loader import render_to_string
from .models import MonitorData, MachineMast, EmpMast, EnrollMast, ReportLog

# Try to import pisa
try:
    from xhtml2pdf import pisa
except ImportError:
    pisa = None  # fallback

def generate_report_for_date(report_date):
    livedatas = MonitorData.objects.filter(PunchDate__date=report_date)
    data = []

    if livedatas.exists():
        srnos = livedatas.values_list('SRNO', flat=True)
        enrollids = livedatas.values_list('EnrollID', flat=True)
        sorted_livedatas = livedatas.order_by('EnrollID', 'PunchDate')

        
        machines = MachineMast.objects.filter(SRNO__in=srnos)
        enrolls = EnrollMast.objects.filter(enrollid__in=enrollids)
        employees = EmpMast.objects.select_related('department', 'company', 'designation', 'enrollid').filter(enrollid__in=enrolls)

        machine_dict = {m.SRNO: m for m in machines}
        enroll_dict = {e.enrollid: e for e in enrolls}
        employee_dict = {e.enrollid_id: e for e in employees}

        for idx, live in enumerate(sorted_livedatas, start=1):  # add serial numbers
            machine = machine_dict.get(live.SRNO)
            if not machine:
                continue
            enroll = enroll_dict.get(live.EnrollID)
            emp_data = employee_dict.get(enroll.id) if enroll else None

            data.append({
                'srno': idx,   # add srno here
                'monitor': live,
                'machine': machine,
                'employee': emp_data
            })

    context = {
        'data': data,
        'selected_date': report_date,
        'total': len(data)
    }

    html = render_to_string('pages/report_pdf.html', context)

    output_dir = 'D:/headcountreport/'
    os.makedirs(output_dir, exist_ok=True)
    pdf_file_path = os.path.join(output_dir, f'report_{report_date}.pdf')

    if pisa:
        with open(pdf_file_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html, dest=pdf_file)
        if pisa_status.err:
            print(f"PDF error on {report_date}")
        else:
            ReportLog.objects.create(date=report_date, Status=1)
    else:
        # fallback: save the HTML if PDF lib is not available
        fallback_html_path = os.path.join(output_dir, f'report_{report_date}.html')
        with open(fallback_html_path, "w", encoding="utf-8") as f:
            f.write(html)
        ReportLog.objects.create(date=report_date, Status=1)
        print(f"xhtml2pdf not installed. Saved as HTML: {fallback_html_path}")

