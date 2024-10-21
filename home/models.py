from django.db import models

# Create your models here.
class MachineMast(models.Model):
    id = models.IntegerField(primary_key=True)
    machineno = models.CharField(max_length=50)
    devicemodel = models.TextField()
    SRNO = models.CharField(max_length=100, unique=True)
    Name = models.TextField()
    Response = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.SRNO

class EnrollMast(models.Model):
    id = models.IntegerField(primary_key=True)
    enrollid = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey('DepartMast', on_delete=models.CASCADE, null=True)
    def __str__(self):
        return str(self.id)

class EmpMast(models.Model): 
    ids = models.BigAutoField(primary_key=True)
    empcode = models.CharField(max_length=100)
    enrollid = models.ForeignKey(EnrollMast, on_delete=models.CASCADE, null=True)
    Cardno = models.CharField(max_length=50)
    Name = models.TextField(blank=True, null=True)
    department = models.ForeignKey('DepartMast', on_delete=models.CASCADE, null=True)
    company = models.ForeignKey('CompanyMast', on_delete=models.CASCADE, null=True)
    designation = models.ForeignKey('DesMast', on_delete=models.CASCADE, null=True)
    Cardstatus = models.BooleanField(default=True)
    Shift = models.CharField(max_length=50)
    CatName = models.TextField(null=True, blank=True)
    STATUS_E = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return str(self.ids)

class MonitorData(models.Model):
    id = models.BigIntegerField(primary_key=True)
    SRNO = models.CharField(max_length=50)
    EnrollID = models.CharField(max_length = 100)
    PunchDate = models.DateTimeField()
    Errorstatus = models.IntegerField(default=0)
    def __str__(self):
        return self.SRNO



class CompanyMast(models.Model):
	CompanyId=models.IntegerField(primary_key=True)
	Company = models.TextField()
	Address = models.TextField()

	def __str__(self):
		return self.CompanyId



class DepartMast(models.Model):
	DepartId = models.IntegerField(primary_key=True)
	DepartName = models.TextField(null=True, blank=True)
	Status = models.TextField(default=True)

	def __str__(self):
		return f"{self.DepartId}"

class DesMast(models.Model):

	Desgid = models.IntegerField(primary_key=True)
	department = models.ForeignKey(DepartMast, on_delete=models.CASCADE, null=True, blank=True)
	Designation = models.TextField()

	def __str__(self):
		return self.Desgid


