from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from home.models import MonitorData, MachineMast, CompanyMast, DepartMast, DesMast, EmpMast, EnrollMast
import pyodbc,datetime 
from django.db import models 
from django.db import connection, transaction
from django.db.models import OuterRef, Subquery
from django.http import JsonResponse
import json
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import logout
from .forms import CompanyForm, MachineForm, DepartForm, DesForm, EmpForm, DateForm, DayForm, InForm, UploadEmployeeForm
from django.db.models.expressions import RawSQL
from django.db.models.functions import Coalesce
from django.db.models import Max
from celery import shared_task
from datetime import timedelta



def home(request):
    if request.session.get('login', None):
        return redirect('dashboard')
    today = timezone.now().date()
    form = DateForm(request.POST or None)
    selected_date = today
    if form.is_valid():
        selected_date = form.cleaned_data['selected_date']
        previous_date = form.cleaned_data['selected_date']
        request.session['previous_date'] = previous_date.strftime("%Y-%m-%d")
    else:
        selected_date = today
    request.session['selected_date'] = selected_date.strftime("%Y-%m-%d")
    with pyodbc.connect(
        'Driver={SQL Server};'
        'Server=DESKTOP-B5D7L9O;'
        'Database=DATAIOCL;'
        'Trusted_Connection=yes;'
    ) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM MonitorDataTbl WHERE CAST(PunchDate AS DATE) = ?"
        punch_datetime = selected_date.strftime('%Y-%m-%d')

        cursor.execute(query, punch_datetime)
        rows = cursor.fetchall()
        
        for row in rows:
            data_dict = {
                'SRNO': row[0],
                'EnrollID': row[1],
                'PunchDate': row[2].strftime("%Y-%m-%d"),
                'TRID': row[3],
                'id': row[4],
                'SEND_SERVER': row[5],
                'RESEND_SERVER': row[6],
            }
            MonitorData.objects.get_or_create(
                id=data_dict['id'],
                defaults={
                    'SRNO': data_dict['SRNO'],
                    'EnrollID': data_dict['EnrollID'],
                    'PunchDate': data_dict['PunchDate'],
                    'TRID':data_dict['TRID']
                }
            )

    livedata = MonitorData.objects.all().order_by('-id')[:10]
    srnos = livedata.values_list('SRNO', flat=True)
    enrollids = livedata.values_list('EnrollID', flat=True)

    machnes = MachineMast.objects.filter(SRNO__in=srnos)
    enrolls = EnrollMast.objects.filter(enrollid__in=enrollids)
    employees = EmpMast.objects.filter(enrollid__in=enrolls)

    machine_dict = {machine.SRNO: machine for machine in machnes}
    enroll_dict = {enroll.enrollid: enroll for enroll in enrolls}
    employee_dict = {employee.enrollid_id: employee for employee in employees}

    data = []
    for live in livedata:
        machine = machine_dict.get(live.SRNO)
        enroll = enroll_dict.get(live.EnrollID)
        employeedata = employee_dict.get(enroll.id) if enroll else None
        data.append({
            'monitor': live,
            'machine': machine,
            'employee': employeedata
        })
    
    monitor_data = MonitorData.objects.filter(PunchDate__date=selected_date).order_by('-id')

    # Initialize all counts
    hazard_in_count = hazard_out_count = 0
    non_hazard_in = non_hazard_out = 0
    wagen_in_count = wagen_out_count = 0
    tank_in_count = tank_out_count = 0
    non_hazard_total = hazard_total = wagen_total = tank_total = 0
    for live in monitor_data:
        machine = MachineMast.objects.filter(SRNO=live.SRNO).first()
        if machine:
            if machine.machineno in ['1', '5']:  # Non-hazard In
                non_hazard_in += 1
            elif machine.machineno in ['2', '6']:  # Non-hazard Out
                non_hazard_out += 1
            elif machine.machineno in ['3', '7']:  # Hazard In
                hazard_in_count += 1
            elif machine.machineno in ['4', '8']:  # Hazard Out
                hazard_out_count += 1

        # Check if EnrollID exists and update total counts accordingly
        if live.EnrollID:
            # Non-hazard total logic
            if machine.machineno in ['1', '5']:
                non_hazard_total += 1
            elif machine.machineno in ['2', '6']:
                non_hazard_total -= 1  # Exit means decrease from total

            # Hazard total logic
            if machine.machineno in ['3', '7']:
                hazard_total += 1
            elif machine.machineno in ['4', '8']:
                hazard_total -= 1  # Exit means decrease from total


            # If the EnrollID is in an "out" machine, check for the last entry
            if machine.machineno in ['2', '6', '4', '8']:

                 # Find last entry for this EnrollID from an "in" machine within 30 seconds before current PunchDate
                last_in_machines = ['1', '5', '3', '7']
                last_in_srnos = MachineMast.objects.filter(machineno__in=last_in_machines).values_list('SRNO', flat=True)

                last_entry = MonitorData.objects.filter(
                    EnrollID=live.EnrollID,
                    PunchDate__lt=live.PunchDate,  # Before the current PunchDate
                    PunchDate__gte=live.PunchDate - timedelta(seconds=30),  # Only within 30 seconds before PunchDate
                    SRNO__in=last_in_srnos
                ).order_by('-PunchDate').first()

                # If no prior "in" entry exists, we need to insert a new record
                if not last_entry:
                    # Find the machine that corresponds to the "in" machine just before the current "out" machine
                    # Get the machine number just before the current one (you'll need a logic or mapping for this)
                    previous_machine_no = None
                    if machine.machineno == '2':
                        previous_machine_no = '1'
                    elif machine.machineno == '6':
                        previous_machine_no = '5'
                    elif machine.machineno == '4':
                        previous_machine_no = '3'
                    elif machine.machineno == '8':
                        previous_machine_no = '7'
                   
                    if previous_machine_no:
                        # Find the SRNO for the previous machine number
                        previous_srno = MachineMast.objects.filter(machineno=previous_machine_no).values_list('SRNO', flat=True).first()

                        if previous_srno:
                            # Insert a new record into MonitorData with PunchDate 30 seconds before the current PunchDate
                            new_punch_date = live.PunchDate - timedelta(seconds=30)
                            last_id = MonitorData.objects.aggregate(max_id=models.Max('id'))['max_id']
                            new_id = (last_id or 0) + 1  # Handle case where table is empty
                            MonitorData.objects.create(
                                id=new_id,  # Use the incremented id
                                EnrollID=live.EnrollID,
                                PunchDate=new_punch_date,
                                SRNO=previous_srno,
                                Errorstatus=1 # Set SRNO to the previous machine's SRNO
                                )

                            # Update counts as required based on the previous machine type
                            if previous_machine_no in ['1', '5']:
                                non_hazard_total += 1  # Non-hazard "in"
                            elif previous_machine_no in ['3', '7']:
                                hazard_total += 1  # Hazard "in"
    # Final calculations if needed, e.g., total headcount calculations
    total_non_hazard_head_count = non_hazard_in - non_hazard_out
    total_hazard_head_count = hazard_in_count - hazard_out_count
    
    context = {
        'form': form,
        'data': data,
        'selected_date': selected_date,
        'hazard_in_count': hazard_in_count,
        'hazard_out_count': hazard_out_count,
        'hazard_total': total_hazard_head_count,

        'non_hazard_in': non_hazard_in,
        'non_hazard_out': non_hazard_out,
        'non_hazard_total': total_non_hazard_head_count,
        
    }
    return render(request, 'pages/index1.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/dashboard/'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid credentials'})
    return render(request, 'pages/list.html')
def logout_view(request):
    logout(request)
    return redirect('list')

def list(request, lists):
    if request.session.get('previous_date'):
        selected_date = request.session.get('previous_date', None)
    else:
        selected_date = request.session.get('selected_date', None)
    
    livedata = MonitorData.objects.filter(PunchDate__date=selected_date)
    srnos = livedata.values_list('SRNO', flat=True)
    enrollids = livedata.values_list('EnrollID', flat=True)
    machnes = MachineMast.objects.filter(SRNO__in=srnos)
    enroll_ids = EnrollMast.objects.filter(enrollid__in=enrollids)
    employees = EmpMast.objects.select_related('department', 'company', 'designation').filter(enrollid__in=enroll_ids)
    machine_dict = {machine.SRNO: machine for machine in machnes}
    employee_dict = {employee.enrollid: employee for employee in employees}
    enroll_dict = {enroll.enrollid: enroll for enroll in enroll_ids}
    
    data = []
    in_ids = set()
    out_ids = set()

    # Identify IN and OUT ids based on machine number
    for live in livedata:
        machine = machine_dict.get(live.SRNO)
        if machine and (machine.machineno == '1' or machine.machineno == '5'):
            in_ids.add(live.EnrollID)
        elif machine and (machine.machineno == '2' or machine.machineno == '6'):
            out_ids.add(live.EnrollID)
        if machine and (machine.machineno == '3' or machine.machineno == '7'):
            in_ids.add(live.EnrollID)
        elif machine and (machine.machineno == '4' or machine.machineno == '8'):
            out_ids.add(live.EnrollID)
    # Populate data with matched employee info
    for live in livedata:
        machine = machine_dict.get(live.SRNO)
        if not machine:
            continue
        
        # Directly use enrollid from livedata to find the employee

        
        enroll_data = enroll_dict.get(live.EnrollID)
        if enroll_data:
            employeedata = employee_dict.get(enroll_data)
        else:
            employeedata = None
       

        if employeedata:
            employee_info = {
                'name': employeedata.Name,
                'empcode': employeedata.empcode,
                'designation': employeedata.designation.Designation,
                'department': employeedata.department.DepartName
            }
        else:
            employee_info = {
                'name': None,
                'designation': None,
                'department': None
            }

        # Modify your condition to include the employee data
        if lists == 'MAIN GATE IN' and (machine.machineno == '1' or machine.machineno == '5'):
            if live.EnrollID in in_ids:
                data.append({
                    'monitor': live,
                    'machine': machine,
                    'employee': employee_info
                })
        elif lists == 'MAIN GATE OUT' and (machine.machineno == '2' or machine.machineno == '6'):
            if live.EnrollID in out_ids:
                data.append({
                    'monitor': live,
                    'machine': machine,
                    'employee': employee_info
                })
        elif lists == 'MAIN GATE TOTAL HEAD COUNT':
            if machine.machineno in ['1', '5']:  # Machines for "IN"
                if live.EnrollID in in_ids and live.EnrollID not in out_ids:
                    data.append({
                        'monitor': live,
                        'machine': machine,
                        'employee': employee_info
                    })
        elif lists == 'GATE3 TOTAL HEAD COUNT':
            if machine.machineno in ['3', '7']:  # Machines for "IN"
                if live.EnrollID in in_ids and live.EnrollID not in out_ids:
                    data.append({
                        'monitor': live,
                        'machine': machine,
                        'employee': employee_info
                    })
        elif lists == 'GATE3 IN' and (machine.machineno == '3' or machine.machineno == '7'):
            if live.EnrollID in in_ids:
                data.append({
                    'monitor': live,
                    'machine': machine,
                    'employee': employee_info
                })
        elif lists == 'GATE3 OUT' and (machine.machineno == '4' or machine.machineno == '8'):
            if live.EnrollID in out_ids:
                data.append({
                    'monitor': live,
                    'machine': machine,
                    'employee': employee_info
                })
       
    context = {
        'data': data,
        'cont': lists,
    }
    return render(request, 'pages/list.html', context)



def index(request,listing):
    # Page from the theme 
    return render(request, 'pages/index.html',{'data':listing})

def report(request):
    today = timezone.now().date()
    form = DayForm(request.POST or None)
    selected_date = today
    filter_type = request.POST.get('flexRadioDefault', 'dateWise')
    data = []

    if form.is_valid():
        selected_date = form.cleaned_data['selected_date']

    context = {
        'form': form,
        'filter_type': filter_type,
        'selected_date': selected_date,
        'machine': MachineMast.objects.all(),
        'employee': EmpMast.objects.all(),
        'department': DepartMast.objects.all(),
    }

    livedata = MonitorData.objects.all()
    srnos = livedata.values_list('SRNO', flat=True)
    enrollids = livedata.values_list('EnrollID', flat=True)
    machines = MachineMast.objects.filter(SRNO__in=srnos)
    enrolls = EnrollMast.objects.filter(enrollid__in=enrollids)
    employees = EmpMast.objects.select_related('department', 'company', 'designation', 'enrollid').filter(enrollid__in=enrolls)
    machine_dict = {machine.SRNO: machine for machine in machines}
    enroll_dict = {enroll.enrollid: enroll for enroll in enrolls}
    employee_dict = {employee.enrollid_id: employee for employee in employees}
    if filter_type == 'dateWise' and selected_date:
        livedatas = MonitorData.objects.filter(PunchDate__date=selected_date)
    elif filter_type == 'gateWise':
        gate_id = request.POST.get('location')
        if gate_id:
            livedatas = MonitorData.objects.filter(SRNO=gate_id)
    elif filter_type == 'employeeWise':
        employee_id = request.POST.get('empcode')
        if employee_id:
            enrolls = EnrollMast.objects.filter(enrollid=employee_id)
            livedatas = MonitorData.objects.filter(EnrollID__in=enrolls)
    elif filter_type == 'departmentWise':
        department_id = request.POST.get('department')
        if department_id:
            emp = EmpMast.objects.select_related('department', 'company', 'designation', 'enrollid').filter(department=department_id)
            enrolls = EnrollMast.objects.filter(id__in=emp.values_list('enrollid', flat=True))
            livedatas = MonitorData.objects.filter(EnrollID__in=enrolls.values_list('enrollid', flat=True))  #
    else:
        livedatas = MonitorData.objects.filter(PunchDate__date=today)

    for live in livedatas:
        machine = machine_dict.get(live.SRNO)
        if not machine:
            continue
        enroll = enroll_dict.get(live.EnrollID)
        employeedata = employee_dict.get(enroll.id) if enroll else None
        data.append({
            'monitor': live,
            'machine': machine,
            'employee': employeedata
        })
    context['data'] = data
    return render(request, 'pages/report.html', context)
  
@login_required
def dashboard(request):
    request.session['login'] = 'adminlogin'
    
    # Get counts using count() method
    emp_count = EmpMast.objects.count()
    depart_count = DepartMast.objects.count()
    designation_count = DesMast.objects.count()

    context = {
        'emp': emp_count,
        'depart_count': depart_count,
        'designation_count': designation_count,
    }

    return render(request, 'pages/dashboard.html', context)
    
def depart_master(request):
    if request.method == 'POST':
        departName = request.POST.get('departName')
        department = DepartMast(DepartName = departName, Status=True)
        department.save()
        return redirect('depart_master')
    departmenties  = DepartMast.objects.all()
    department_list = [{'counter': i + 1, 'department': department} for i, department in enumerate(departmenties )]
    context = {
        'department_list': department_list
    }
    return render(request,'pages/depart_master.html',context)

def edit_depart(request, pk):
    department = get_object_or_404(DepartMast, pk=pk)
    if request.method == 'POST':
        form = DepartForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('depart_master')
    else:
        form = DepartForm(instance=department)
    return render(request, 'pages/edit_depart.html', {'form': form})

def delete_depart(request, pk):
    department = get_object_or_404(DepartMast, pk=pk)
    department.delete()
    return redirect('depart_master')


def emp_master(request):
    if request.method == 'POST':
        empcode = request.POST.get('empcode')
        enrollid = request.POST.get('enrollid')
        Name = request.POST.get('Name')
        compid = request.POST.get('compid')
        DepartId = request.POST.get('DepartId')
        Desgid = request.POST.get('Desgid')
        try:
            enrollid = EnrollMast.objects.get(id=enrollid)
            company = CompanyMast.objects.get(CompanyId=compid)
            department = DepartMast.objects.get(DepartId=DepartId)
            designation = DesMast.objects.get(Desgid=Desgid)
            
            if not EmpMast.objects.filter(enrollid=enrollid).exists():
                if not EmpMast.objects.filter(empcode=empcode).exists():
                    employee = EmpMast(company=company, department=department, designation=designation, empcode=empcode, Name=Name, enrollid=enrollid)
                    employee.save()
                    messages.success(request, 'Employee saved successfully! {}'.format(enrollid.enrollid))
                else:
                    messages.error(request, 'Employee already exists {}'.format(enrollid.enrollid))
        except EnrollMast.DoesNotExist:
            messages.error(request, 'Invalid employee EmployeeID')

        return redirect('emp_master')

    # Fetch data that does not have a matching entry in EmpMast
    existing_enrollid = EmpMast.objects.values_list('enrollid', flat=True)
    enrollid = EnrollMast.objects.exclude(id__in=existing_enrollid)
    departlist = DepartMast.objects.all()
    complist = CompanyMast.objects.all()
    designationlist = DesMast.objects.select_related('department').all()
    employeedatalist = EmpMast.objects.select_related('department', 'company', 'designation', 'enrollid')

    employeedata_list = [{'counter': i + 1, 'employeelist': employeelist} for i, employeelist in enumerate(employeedatalist)]
    existing_enroll_ids = EmpMast.objects.values_list('enrollid_id', flat=True)
    enrollid_queryset = EnrollMast.objects.exclude(id__in=existing_enroll_ids)
      # Assuming foreign key
    enroll_dict = {}
    for department in departlist:
        enroll_dict[department.DepartId] = enrollid_queryset.filter(department__DepartId=department.DepartId)
    
    designation_dict = {}
    for desg in designationlist:
        depart_id = desg.department.DepartId
        if depart_id not in designation_dict:
            designation_dict[depart_id] = []
        designation_dict[depart_id].append({
            'Desgid': desg.Desgid,
            'Designation': desg.Designation
        })

    context = {
        'departlist': departlist,
        'complist': complist,
        'designation_dict': designation_dict,
        'emplist': employeedata_list,
        'enroll_dict': enroll_dict  # Pass the enroll_dict to the template
    }

    return render(request, 'pages/emp_master.html', context)

def get_departments_by_enrollid(request):
    enrollid = request.GET.get('enrollid')
    if enrollid:
        try:
            enroll = EnrollMast.objects.get(id=enrollid)
            departments = DepartMast.objects.filter(enroll=enroll)  # Adjust the query as per your model relationships
            department_data = [{'DepartId': dept.DepartId, 'DepartName': dept.DepartName} for dept in departments]
            return JsonResponse({'departments': department_data}, safe=False)
        except EnrollMast.DoesNotExist:
            return JsonResponse({'error': 'Invalid EnrollID'}, status=400)
    return JsonResponse({'error': 'No EnrollID provided'}, status=400)
def get_enrollid_by_department(request):
    depart_id = request.GET.get('DepartId')
    if depart_id:
        try:
            # Get existing enroll IDs from EmpMast
            existing_enroll_ids = EmpMast.objects.values_list('enrollid_id', flat=True)

            # Filter EnrollMast by the department and exclude existing EnrollID
            enrolls = EnrollMast.objects.exclude(id__in=existing_enroll_ids).filter(department_id=depart_id)

            # Prepare the response data
            enroll_data = [{'id': enroll.id, 'enrollid': enroll.enrollid} for enroll in enrolls]
            return JsonResponse({'enrolls': enroll_data}, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)  # Catching a general exception for simplicity
    return JsonResponse({'error': 'No DepartmentID provided'}, status=400)

def edit_employee(request, pk):
    employe = get_object_or_404(EmpMast, pk=pk)
    if request.method == 'POST':
        form = EmpForm(request.POST, instance=employe)
      
        if form.is_valid():
            employee = form.save(commit=False)
            # enroll = EnrollMast.objects.get(EnrollID=request.POST.get('enrollid'))
            deparment = DepartMast.objects.get(DepartId=request.POST.get('department'))
            designation = DesMast.objects.get(Desgid=request.POST.get('designation'))
            employee.deparment = deparment
            employee.save()
            employee.designation = designation
            employee.save()
            return redirect('emp_master')
    else:   
        form = EmpForm(instance=employe) 
   
    departlist = DepartMast.objects.all()
    designationlist = DesMast.objects.select_related('department').all()
    designation_dict = {}
    for desg in designationlist:
        depart_id = desg.department.DepartId
        if depart_id not in designation_dict:
            designation_dict[depart_id] = []
        designation_dict[depart_id].append({
            'Desgid':desg.Desgid,
            'Designation': desg.Designation
            })
    return render(request, 'pages/edit_employee.html', {'form': form,'designationlist':designationlist, 'designation_dict' : designation_dict,  'departlist' : departlist,})

def delete_employee(request, pk):
    employee = get_object_or_404(EmpMast, pk=pk)
    employee.delete()
    return redirect('emp_master')

def enroll_mast(request):
    if request.method == 'POST':
        DepartId = request.POST.get('DepartId')

        try:
            department = DepartMast.objects.get(DepartId=DepartId)
            
            # Check if DepartId is '1' (or any specific condition)
            if DepartId == '5':
                enrollid = request.POST.get('enrollid')  # Get enrollid instead of from/to
                if not EnrollMast.objects.filter(enrollid=enrollid).exists():
                    enrollmast = EnrollMast(enrollid=enrollid, department=department)
                    enrollmast.save()
                    messages.success(request, 'Success Enrollid Entry')
                else:
                    messages.error(request, 'Duplicate Enrollid Entry')
            else:
                from_status = int(request.POST.get('froms'))
                to_status = int(request.POST.get('to'))
                if not EnrollMast.objects.filter(enrollid=from_status).exists():
                    # Create EnrollMast objects within the range
                    for i in range(from_status, to_status + 1):
                        enrollmast = EnrollMast(enrollid=i, department=department)
                        enrollmast.save()
                        messages.success(request, 'Success Enrollid Entry')
                else:
                    messages.error(request, 'Duplicate data provided')

            return redirect('enroll_mast')

        except (ValueError, TypeError, DepartMast.DoesNotExist):
            # Handle errors
            context = {'error': 'Invalid data provided'}
            messages.error(request, 'Invalid data provided')
            return render(request, 'pages/enroll_mast.html', context)

    # Fetch all departments and enrollments
    departlist = DepartMast.objects.all()
    enrolllisties = EnrollMast.objects.select_related('department')

    enrollid_list = [{'counter': i + 1, 'enrolllist': enrolllist} for i, enrolllist in enumerate(enrolllisties)]
    
    context = {
        'enrollid_list': enrollid_list,
        'departlist': departlist
    }

    return render(request, 'pages/enroll_mast.html', context)

def delete_enroll(request, pk):
    employee = get_object_or_404(EnrollMast, pk=pk)
    employee.delete()
    return redirect('enroll_mast')

def des_master(request):
    if request.method == 'POST':
        DepartId = request.POST.get('DepartId')
        Designation = request.POST.get('Designation')
        department = DepartMast.objects.get(DepartId=DepartId)
        designation = DesMast(department=department, Designation=Designation)
        designation.save()
        return redirect('des_master')
    designationies = DesMast.objects.select_related('department').all()
    departlist = DepartMast.objects.all()
    designation_list = [{'counter': i + 1, 'designation': designation} for i, designation in enumerate(designationies)]
    context = {
    'designation_list': designation_list,
    'departlist' : departlist
    }
    return render(request,'pages/des_master.html',context)
    

def edit_designation(request, pk):
    designation = get_object_or_404(DesMast, pk=pk)
    if request.method == 'POST':
        form = DesForm(request.POST, instance=designation)
        if form.is_valid():
            designation = form.save(commit=False)
            department = DepartMast.objects.get(DepartId=request.POST.get('department'))
            designation.department = department
            designation.save()
            return redirect('des_master')
    else:   
        form = DesForm(instance=designation)
    departlist = DepartMast.objects.all()
    return render(request, 'pages/edit_designation.html', {'form': form, 'departlist': departlist})

def delete_designation(request, pk):
    designation = get_object_or_404(DesMast, pk=pk)
    designation.delete()
    return redirect('des_master')

def comp_master(request):
    if request.method == 'POST':
        Company = request.POST.get('Company')
        Address = request.POST.get('Address')
        company =CompanyMast(Company = Company,Address = Address)
        company.save()
        return redirect('comp_master')
    companies  = CompanyMast.objects.all()
    company_list = [{'counter': i + 1, 'company': company} for i, company in enumerate(companies )]
    context = {
        'company_list': company_list
    }
    return render(request,'pages/comp_master.html',context)

def edit_company(request, pk):
    company = get_object_or_404(CompanyMast, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('comp_master')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'pages/edit_company.html', {'form': form})

def delete_company(request, pk):
    company = get_object_or_404(CompanyMast, pk=pk)
    company.delete()
    return redirect('comp_master')

def machine_master(request):
    if request.method == 'POST':
        machineno = request.POST.get('machineno')
        SRNO = request.POST.get('SRNO')
        devicemodel = request.POST.get('devicemodel')
        Name = request.POST.get('Name')
        Response = request.POST.get('Response')
        machine =MachineMast(machineno=machineno, SRNO= SRNO, devicemodel=devicemodel, Name = Name, Response = Response)
        machine.save()
        return redirect('machine_master')
    machines  = MachineMast.objects.all()
    machine_list = [{'counter': i + 1, 'machine': machine} for i, machine in enumerate(machines)]
    context = {
        'machine_list': machine_list
    }
    return render(request,'pages/machine_master.html',context)
def edit_machine(request, pk):
    machine = get_object_or_404(MachineMast, pk=pk)
    if request.method == 'POST':
        form = MachineForm(request.POST, instance=machine)
        if form.is_valid():
            form.save()
            return redirect('machine_master')
    else:
        form = MachineForm(instance=machine)
    return render(request, 'pages/edit_machine.html', {'form': form})

def delete_machine(request, pk):
    machine = get_object_or_404(MachineMast, pk=pk)
    machine.delete()
    return redirect('machine_master')


def category(request):
    today = timezone.now().date()
    form = DateForm(request.POST or None)
    selected_date = today

    if form.is_valid():
        selected_date = form.cleaned_data['selected_date']
        request.session['default_date'] = selected_date.strftime("%Y-%m-%d")

    if request.session.get('default_date'):
        selected_date = request.session.get('default_date', None)
    else:
        request.session['selected_date'] = selected_date.strftime("%Y-%m-%d")
        selected_date = request.session.get('selected_date', None)
   
    livedata = MonitorData.objects.filter(PunchDate__date=selected_date)
    srnos = livedata.values_list('SRNO', flat=True)
    enrollids = livedata.values_list('EnrollID', flat=True)
    
    # Fetch machines and employees
    machines = MachineMast.objects.filter(SRNO__in=srnos)
    enroll_ids = EnrollMast.objects.filter(enrollid__in=enrollids)
    employees = EmpMast.objects.select_related('department').filter(enrollid__in=enroll_ids)
    departments = DepartMast.objects.all()

    # Create dictionaries for easy access
    machine_dict = {machine.SRNO: machine for machine in machines}
    employee_dict = {employee.enrollid: employee for employee in employees}
    enroll_dict = {enroll.enrollid: enroll for enroll in enroll_ids}

    # Prepare data by gates
    gate_data = {
        'main_gate': [],
        'gate3': [],
        
    }

    in_ids = set()
    out_ids = set()

    # Identify IN and OUT ids based on machine number
    for live in livedata:
        machine = machine_dict.get(live.SRNO)
        if machine:
            if machine.machineno in ['1', '5']:
                in_ids.add(live.EnrollID)
            elif machine.machineno in ['2', '6']:
                out_ids.add(live.EnrollID)
            elif machine.machineno in ['3', '7']:
                in_ids.add(live.EnrollID)
            elif machine.machineno in ['4', '8']:
                out_ids.add(live.EnrollID)

    # Populate gate-specific data
    for live in livedata:
        machine = machine_dict.get(live.SRNO)
        if not machine:
            continue

        enroll_data = enroll_dict.get(live.EnrollID)
        employeedata = employee_dict.get(enroll_data) if enroll_data else None

        employee_info = {
            'empcode': employeedata.empcode if employeedata else None,
            'department': employeedata.department.DepartName if employeedata else None
        }
       
        if machine.machineno in ['1', '5'] and live.EnrollID in in_ids and live.EnrollID not in out_ids:
            gate_data['main_gate'].append({'monitor': live, 'machine': machine, 'employee': employee_info})
        elif machine.machineno in ['3', '7'] and live.EnrollID in in_ids and live.EnrollID not in out_ids:
            gate_data['gate3'].append({'monitor': live, 'machine': machine, 'employee': employee_info})
    print(gate_data)
        # print('gate_data', len(gate_data['main_gate']))
        # print('hazardous_gate', len(gate_data['hazardous_gate']))  
        # print('wagen_gate', len(gate_data['wagen_gate']))
        # print('tank_farm', (gate_data['tank_farm']))  
    # Prepare the context with department-wise data
    context = {
        'data': gate_data,
        'form': form,
        'departments': departments
    }
    return render(request, 'pages/category.html', context)


def con_mismatch(request):
    today = timezone.now().date()
    form = DateForm(request.POST or None)
    inputs = InForm(request.POST or None)
    selected_date = today
    selected_input = None

    if form.is_valid():
        selected_date = form.cleaned_data['selected_date']

    if inputs.is_valid():
        selected_input = inputs.cleaned_data['selected_input']

    # Fetch MonitorData for the selected date
    monitor_data = MonitorData.objects.filter(PunchDate__date=selected_date)

    # Logic to find continuous exit entries
    mismatched_data = []
    for data in monitor_data:
        mach = MachineMast.objects.filter(SRNO=data.SRNO).first()

        if mach and mach.Response == 'EXIT':
            previous_entries = MonitorData.objects.filter(EnrollID=data.EnrollID, PunchDate__lt=data.PunchDate).order_by('-PunchDate')

            if previous_entries.exists():
                previous_entry = previous_entries.first()
                previous_mach = MachineMast.objects.filter(SRNO=previous_entry.SRNO).first()

                if previous_mach and previous_mach.Response == 'EXIT':
                    enroll = EnrollMast.objects.filter(enrollid=data.EnrollID).first()
                    employee = EmpMast.objects.get(enrollid=enroll)
                    mismatched_data.append({
                        'entry': mach.Name,
                        'response': mach.Response,
                        'enrollid': data.EnrollID,
                        'name': employee.Name,
                        'out_time': data.PunchDate.strftime("%H:%M"),
                        'previous_out_time': previous_entry.PunchDate.strftime("%H:%M"),
                    })

                    # Optionally update the hazardous_in time
                    # data.hazardous_in = previous_entry.hazardous_out
                    # data.save()

    context = {
        'form': form,
        'inputs': inputs,
        'selected_date': selected_date,
        'selected_input': selected_input,
        'mismatched_data': mismatched_data,
    }

    if request.method == 'POST' and 'action' in request.POST:
        enrollid = request.POST.get('enrollid')
        gate = request.POST.get('gate')
        response = request.POST.get('response')
        in_time = request.POST.get('in_time')

        # Insert new data into MonitorData table
        new_data = MonitorData(
            EnrollID=enrollid,
            SRNO=gate,
            Response='EXIT',
            PunchDate=timezone.now().replace(hour=int(in_time.split(':')[0]), minute=int(in_time.split(':')[1]), second=int(in_time.split(':')[2]))
        )
        new_data.save()

        return redirect('con_mismatch')  # Redirect to the same page to see updated list

    return render(request, 'pages/con_mismatch.html', context)
@login_required
def upload_employee_data(request):
    if request.method == 'POST':
        form = UploadEmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            department = form.cleaned_data['department']
            designation = form.cleaned_data['designation']
            
            try:
                # Read the Excel file into a pandas DataFrame
                df = pd.read_excel(file)
                
                for _, row in df.iterrows():
                    # Assuming the columns in the Excel file match the fields in the model
                    EmpMast.objects.update_or_create(
                        empcode=row['empcode'],  # Use empcode as the unique identifier
                        defaults={
                            'Cardno': row['Cardno'],
                            'Name': row['Name'],
                            'enrollid': row['enrollid'],  # Ensure this matches EnrollMast in your DB
                            'Cardstatus': row['Cardstatus'],
                            'Shift': row['Shift'],
                            'CatName': row['CatName'],
                            'STATUS_E': row['STATUS_E'],
                            'department': department,  # Static from the form
                            'designation': designation,  # Static from the form
                        }
                    )
                
                messages.success(request, 'Employee data updated successfully!')
                return redirect('upload_employee_data')

            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                return redirect('upload_employee_data')

    else:
        form = UploadEmployeeForm()

    return render(request, 'pages/upload_employee.html', {'form': form})
def in_console(request):
    today = timezone.now().date()
    form = DateForm(request.POST or None)
    inputs = InForm(request.POST or None)
    selected_date = today
    selected_input = None

    if form.is_valid():
        selected_date = form.cleaned_data['selected_date']

    if inputs.is_valid():
        selected_input = inputs.cleaned_data['selected_input']

    # Fetch MonitorData for the selected date and ErrorStatus=1
    monitor_data = MonitorData.objects.filter(PunchDate__date=selected_date, Errorstatus=1)

    # Store data grouped by gate
    gate_wise_data = []
    
    for data in monitor_data:
        # Find the corresponding gate machine entry
        mach = MachineMast.objects.filter(SRNO=data.SRNO).first()
        if not mach:
            continue
        
        # Find previous 'OUT' entry (if any) for the same employee and gate
        previous_entries = MonitorData.objects.filter(
            EnrollID=data.EnrollID, PunchDate__lt=data.PunchDate
        ).order_by('-PunchDate')

        in_time = data.PunchDate.strftime("%H:%M:%S") if mach.Response == 'IN' else None
        out_time = None
        previous_mach_name = None

        if previous_entries.exists():
            previous_entry = previous_entries.first()
            previous_mach = MachineMast.objects.filter(SRNO=previous_entry.SRNO).first()

            if previous_mach and previous_mach.Response == 'EXIT':
                out_time = previous_entry.PunchDate.strftime("%H:%M:%S")
                previous_mach_name = previous_mach.Name

        enroll = EnrollMast.objects.filter(enrollid=data.EnrollID).first()
        if enroll:
            try:
                employee = EmpMast.objects.get(enrollid=enroll)
                department = employee.department  # Assuming department field exists in EmpMast
                # Collect gate-wise IN and OUT times
                gate_wise_data.append({
                    'gate_name': mach.Name,  # Gate name
                    'in_time': in_time,
                    'out_time': out_time,
                    'enrollid': data.EnrollID,
                    'name': employee.Name,
                    'department': department,  # Department name
                    'previous_gate_name': previous_mach_name,
                })
            except EmpMast.DoesNotExist:
                # Handle the case where the employee does not exist
                print(f"Employee with EnrollID {enroll.enrollid} does not exist.")


    context = {
        'form': form,
        'inputs': inputs,
        'selected_date': selected_date,
        'selected_input': selected_input,
        'gate_wise_data': gate_wise_data,
    }

    return render(request, 'pages/in_console.html', context)
