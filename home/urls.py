from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('index/<str:listing>', views.index, name='index'),
    path('list/<str:lists>', views.list, name='list'),
    path('report/', views.report, name='report'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('depart_master/',views.depart_master, name='depart_master'),
    path('edit/<int:pk>/', views.edit_depart, name='edit_depart'),
    path('delete/<int:pk>/', views.delete_depart, name='delete_depart'),
    path('emp_master/',views.emp_master, name='emp_master'),
    path('des_master/',views.des_master, name='des_master'),
    path('comp_master/',views.comp_master, name='comp_master'),
    path('machine_master/',views.machine_master, name='machine_master'),
    path('enroll_mast/',views.enroll_mast, name='enroll_mast'),
    path('delete_enroll/<int:pk>/', views.delete_enroll, name='delete_enroll'),
    path('edit_company/<int:pk>/', views.edit_company, name='edit_company'),
    path('delete_company/<int:pk>/', views.delete_company, name='delete_company'),
    path('edit_machine/<int:pk>/', views.edit_machine, name='edit_machine'),
    path('delete_machine/<int:pk>/', views.delete_machine, name='delete_machine'),
    path('edit_employee/<int:pk>/', views.edit_employee, name='edit_employee'),
    path('delete_employee/<int:pk>/', views.delete_employee, name='delete_employee'),
    path('edit_designation/<int:pk>/', views.edit_designation, name='edit_designation'),
    path('delete_designation/<int:pk>/', views.delete_designation, name='delete_designation'),
    path('category/',views.category, name='category'),
    path('con_mismatch/',views.con_mismatch,name='con_mismatch'),
    path('in_console/',views.in_console,name='in_console'),
    path('upload/', views.upload_employee_data, name='upload_employee_data'),
    path('get_departments_by_enrollid/', views.get_departments_by_enrollid, name='get_departments_by_enrollid'),
    path('get_enrollid_by_department/', views.get_enrollid_by_department, name='get_enrollid_by_department'),

]
