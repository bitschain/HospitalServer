from django.http import response
from django.http.response import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import DocumentType, Employee, Report, Visit, mst_Patient
from umbral import capsule, encrypt, PublicKey
import json
import base64


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
                "visit_id": latest_visit.visit_id,
                "qr_string": str(latest_visit.visit_id) + str(body["employeeId"]) + latest_visit.session_public_key
            }       
            return JsonResponse(qr_json)
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
    serialized_pub_key = visit.session_public_key
    pub_key_bytes = base64.b64decode(serialized_pub_key.encode('utf-8'))
    pk = PublicKey._from_exact_bytes(data=pub_key_bytes)
    capsule, encrypted_document = encrypt(pk, document.encode())
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
                capsule, encrypted_document = get_encrypted_document(report.first().document, visit.first())
                return JsonResponse({
                    'encrypted_document': encrypted_document,
                    'capsule': capsule
                })
            return HttpResponseBadRequest("No Report exists with given ReportId")
        return HttpResponseBadRequest("No Visit exists with given VisitId")
    return HttpResponseBadRequest("Request should be a GET request")

@csrf_exempt
def get_documents(request):
    if request.method == 'GET':
        visit_id = request.GET.get('visit_id', -1)
        report_ids = request.GET.get('report_ids', [])
        visit = Visit.objects.filter(visit_id=visit_id)
        if visit.exists():
            response = []
            for report_id in report_ids:
                report_dict = {}
                report = Report.objects.filter(report_id=report_id)
                if report.exists():
                    capsule, encrypted_document = get_encrypted_document(report.first().document, visit.first())
                    report_dict['report_id'] = report_id
                    report_dict['encrypted_document'] = base64.b64encode(encrypted_document).decode('utf-8')
                    report_dict['capsule'] = base64.b64encode(bytes(capsule)).decode('utf-8')
                else:
                    report_dict['report_id'] = report_id
                    report_dict['encrypted_document'] = ''
                    report_dict['capsule'] = ''
                response.append(report_dict)
            return JsonResponse({'result': response})
        return HttpResponseBadRequest("No visit with this visitId exists")
    return HttpResponseBadRequest("Request should be a get request")