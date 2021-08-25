from django.http.response import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import DocumentType, Employee, Report, Visit, mst_Patient
from umbral import capsule, encrypt
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

@csrf_exempt
def generate_qr_string(request):
    if request.method == 'POST':
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            patient = mst_Patient.objects.filter(patient_id = body["patientId"])
        except mst_Patient.DoesNotExist:
            return HttpResponse(status=404)
        if patient.exists():
            try:
                latest_visit = Visit(session_public_key = body["publicKey"], patient_id = patient.first())
                latest_visit.save()
            except Visit.DoesNotExist:
                return HttpResponse(status=404)
            proxy_server = 'proxy.com'
            hospital_server = 'hospital.com'
            qr_json = {
                "proxy_server": proxy_server, 
                "hospital_server": hospital_server, 
                "generated_by": body["employeeId"], 
                "session_public_key": latest_visit.session_public_key, 
                "visit_id": latest_visit.visit_id
            }       
            return HttpResponse(json.dumps(qr_json))
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

def get_encrypted_document(document, visit):
    capsule, encrypted_document = encrypt(visit.session_public_key, document.encode())
    return capsule, encrypted_document

#TODO
@csrf_exempt
def download_document(request):
    if request.method == 'GET':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        visit = Visit.objects.filter(visit_id=body["visitId"])
        report = Report.objects.filter(report_id=body["reportId"])
        if visit.exists():
            if report.exists():
                capsule, encrypted_document = get_encrypted_document(report.document, visit)
                return JsonResponse({
                    'encrypted_document': encrypted_document,
                    'capsule': capsule
                })
            return HttpResponseBadRequest("No Report exists with given ReportId")
        return HttpResponseBadRequest("No Visit exists with given VisitId")
    return HttpResponseBadRequest("Request should be a GET request")

@csrf_exempt
def send_encrypted_documents_to_proxy(request):
    if request.method == 'GET':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        visit = Visit.objects.filter(visit_id=body['visitId'])
        if visit.exists():
            report_ids = body["reportIds"]
            encrypted_documents = []
            capsules = []
            for report_id in report_ids:
                report = Report.objects.filter(report_id=report_id)
                if report.exists():
                    capsule, encrypted_document = get_encrypted_document(report.first().document, visit)
                    encrypted_documents.append(encrypted_document)
                    capsules.append(capsule)
                else:
                    encrypted_documents.append(None)
                    capsules.append(None)
            return JsonResponse({
                'encrypted_documents': encrypted_documents,
                'capsules': capsules
            })
        return HttpResponseBadRequest("No visit with this visitId exists")
    return HttpResponseBadRequest("Request should be a get request")