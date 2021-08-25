from django.http.response import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import DocumentType, Employee, Report, Visit, mst_Patient
import json

# Create your views here.
@csrf_exempt
def createNewUserSession(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        patient = mst_Patient.objects.filter(patient_id = body["patientId"])
        if patient.exists():
            visit = Visit(session_public_key = body["publicKey"], patient_id = patient.first())
            visit.save()
            return HttpResponse("Session Created")
        return HttpResponseBadRequest("Patient doesn't exist")
    return HttpResponseBadRequest("Request should be a post request")

def uploadDocument(document, visit, employee):
    # try:
    documentType = DocumentType.objects.filter(document_id=document['documentType']).first()
    report = Report(visit_id=visit, document=document['document'], created_employee=employee, updated_employee=employee, document_type=documentType)
    report.save()
    return report.report_id
    # except:
      #  return -1

@csrf_exempt
def uploadDocumentBatch(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        visit = Visit.objects.filter(visit_id=body['visitId'])
        employee = Employee.objects.filter(employee_id=body['employeeId'])
        if visit.exists():
            if employee.exists():
                listOfDocuments = body['documents']
                reportIds = []
                for index, document in enumerate(listOfDocuments):
                    if DocumentType.objects.filter(document_id=document['documentType']).exists():
                        id = uploadDocument(document, visit.first(), employee.first())
                        reportIds.append(id)
                    else:
                        reportIds.append(-1)
                return JsonResponse({'reportIds': reportIds})
            return HttpResponseBadRequest("No Employee with given EmployeeId")
        return HttpResponseBadRequest("No visit with corrosponding visitId")
    return HttpResponseBadRequest("Request should be post and not get")

