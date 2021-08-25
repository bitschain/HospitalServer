from django.contrib import admin
from .models import DocumentType, Employee, Report, Visit, mst_Department, mst_EmployeeType, mst_Patient

# Register your models here.
admin.site.register(mst_Patient)
admin.site.register(mst_Department)
admin.site.register(mst_EmployeeType)
admin.site.register(Employee)
admin.site.register(Visit)
admin.site.register(DocumentType)
admin.site.register(Report)
