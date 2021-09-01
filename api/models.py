from django.db import models
from django.db.models.deletion import CASCADE

# Create your models here.
class mst_Patient(models.Model):
    patient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class mst_Department(models.Model):
    departmenet_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

class mst_EmployeeType(models.Model):
    employee_type_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50)

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey('mst_Department', on_delete=CASCADE)
    type = models.ForeignKey('mst_EmployeeType', on_delete=CASCADE)

class Visit(models.Model):
    visit_id = models.AutoField(primary_key=True)
    session_public_key = models.TextField()
    patient_id = models.ForeignKey('mst_Patient', on_delete=CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

class DocumentType(models.Model):
    document_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    visit_id = models.ForeignKey('Visit', on_delete=CASCADE)
    document = models.TextField()
    created_employee = models.ForeignKey('Employee', related_name='report_created_employee_id', on_delete=CASCADE)
    updated_employee = models.ForeignKey('Employee', related_name='report_updated_employee_id', on_delete=CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    document_type = models.ForeignKey('DocumentType', on_delete=CASCADE)
    # # We might have multiple hash addresses in the future
    # hash_account_address = models.TextField(blank=True)
    # # -1 index represents that the index has not yet been assigned
    # hash_index = models.IntegerField(default=-1)