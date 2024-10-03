from django import forms
from django.forms import ModelChoiceField
from .models import CompanyMast, MachineMast, DepartMast, DesMast, EmpMast,MonitorData
import datetime


class CompanyForm(forms.ModelForm):
    class Meta:
        model = CompanyMast
        fields = ['Company', 'Address']

class MachineForm(forms.ModelForm):
    class Meta:
        model = MachineMast
        fields = ['SRNO','devicemodel','machineno','Name','Response']

class DepartForm(forms.ModelForm):
    class Meta:
        model = DepartMast
        fields = ['DepartName']

class DesForm(forms.ModelForm):
    class Meta:
        model = DesMast
        fields = ['Designation','department']

class EmpForm(forms.ModelForm):
    empcode = ModelChoiceField(queryset=MonitorData.objects.all(), required=True)
    class Meta:
        model = EmpMast
        fields = ['empcode','Name','department','designation']

class DateForm(forms.Form):
    selected_date = forms.DateField(
        initial=datetime.date.today,widget=forms.DateInput(attrs={
            'type': 'date',
            'style': 'height: 35px; font-size: 20px; padding: 5px; border: 1px solid #ccc; border-radius: 8px; margin-bottom: 25px;'
        })
    )

class DayForm(forms.Form):
    selected_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class':'form-control'}))
class InForm(forms.Form):
    selected_input = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control','style':'border: 1px solid #ccc;'})
    )
class UploadEmployeeForm(forms.Form):
    file = forms.FileField(label='Select an Excel file')
    department = forms.ModelChoiceField(queryset=DepartMast.objects.all(), label='Department', required=True)
    designation = forms.ModelChoiceField(queryset=DesMast.objects.all(), label='Designation', required=True)
    