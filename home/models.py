from django.db import models
from django.db.models import Q

# Create your models here.
class GatePass(models.Model):
    allowing_entry = models.CharField(max_length=10, choices=[('Yes', 'Hazardous Area'), ('No', 'Non Hazardous Area')])
    id = models.IntegerField(primary_key=True)
    cardNo                       = models.CharField(max_length=250,blank=False,null=False)
    date                         = models.DateField(null=True, blank=True)
    name                         = models.CharField(max_length=250,blank=True, null=True)
    company                      = models.CharField(max_length=250,blank=True, null=True)
    address                      = models.CharField(max_length=250,blank=True,null=True)
    mobile                       = models.CharField(max_length=250,blank=True, null=True)
    vehicleNo                    = models.CharField(max_length=250,blank=True, null=True)
    purpose                      = models.TextField()
    visitor_name                      = models.TextField()
    noOfPerson                   = models.CharField(max_length=250,blank=True,null=True)
    idNo                         = models.CharField(max_length=250,blank=True,null=True)
    typeOf                       = models.CharField(max_length=250,blank=True,null=True)
    govt_id                      = models.CharField(max_length=250,blank=True,null=True)
    govtno                       = models.CharField(max_length=250,blank=True,null=True)
    personToMeet                 = models.CharField(max_length=250,blank=True,null=True)
    inTime                       = models.CharField(max_length=250,blank=True,null=True)
    outTime                      = models.CharField(max_length=250,blank=True,null=True)
    permittedBy                  = models.CharField(max_length=250,blank=True,null=True)
    carringGadget                = models.CharField(max_length=250,blank=True,null=True)
    passNo                       = models.CharField(max_length=250,blank=True,null=True)
    image                        = models.ImageField(upload_to="gatepass_images/", default="default.jpg")
    remarks = models.TextField(blank=True, null=True) 
    valid_from                   = models.DateTimeField(null=True, blank=True)
    valid_to                     = models.DateTimeField(null=True, blank=True)
    renew_remarks=models.TextField(max_length=250,blank=True,null=True)
    createdAt                    = models.DateField(null=True, blank=True)
    updatedAt                    = models.DateField(null=True, blank=True)
    status                       = models.CharField(max_length=250, default='true')
    def __str__(self):
            return f"GatePass {self.id}"
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
        return str(self.empcode)

class MonitorData(models.Model):
    id = models.BigIntegerField(primary_key=True)
    SRNO = models.CharField(max_length=50)
    EnrollID = models.CharField(max_length = 100)
    PunchDate = models.DateTimeField()
    TRID= models.CharField(max_length=50)
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
		return f"{self.DepartName}"

class DesMast(models.Model):

	Desgid = models.IntegerField(primary_key=True)
	department = models.ForeignKey(DepartMast, on_delete=models.CASCADE, null=True, blank=True)
	Designation = models.TextField()

	def __str__(self):
		return self.Desgid
      
class ReportLog(models.Model):
    Id = models.AutoField(primary_key=True)
    date = models.DateField()  
    addedon = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    Status = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.date}"