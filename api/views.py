from hospital_server.settings import HOSPITAL_ID, HOSPITAL_PRIVATE_KEY, HOSPITAL_PUBLIC_KEY, SMART_CONTRACT_ENDPOINT
from django.http import response
from django.http.response import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import DocumentType, Employee, Report, Visit, mst_Patient
from umbral import Capsule, encrypt, PublicKey, decrypt_reencrypted, CapsuleFrag, SecretKey
from django.conf import settings
import json, base64, hashlib, requests

# hospital_b_public_key_utf8="A8oaMaPq0YNLGUJ3n3i3KCbrIyFiCNwdkH872O31mRXE"
# hospital_b_secret_key_utf8="lal4unkPcwkHLl0Epgr35YYBBQVgCr8Ql8Wn2Pba7hs="
# Create your views here.

        
@csrf_exempt
def createNewUserSession(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        # patient = mst_Patient.objects.filter(patient_id = body["patientId"])
        # if patient.exists():
        visits = Visit.objects.filter(visit_id=body["visitId"])
        if visits.exists():
            visit = visits.first()
            visit.session_public_key = body["sessionPublicKey"]
            visit.save()
            return HttpResponse("Session Created")
        return HttpResponseBadRequest("Visit doesn't exist")
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
                employees = Employee.objects.filter(employee_id=body["employeeId"])
                if employees.exists():
                    employee = employees.first()
                    latest_visit = Visit(session_public_key = "", patient_id = patient.first(), employee = employee)
                    latest_visit.save()
                else:
                    return HttpResponseBadRequest("Employee doesn't exist")
            except Visit.DoesNotExist:
                return HttpResponse(status=404)
            qr_json = {
                "proxy_server": settings.PROXY_URL, 
                "hospital_server": settings.HOSPITAL_URL, 
                "generated_by": body["employeeId"],
                "visit_id": latest_visit.visit_id
            }       
            return JsonResponse(qr_json)
        return HttpResponseBadRequest("Patient doesn't exist")
    return HttpResponseBadRequest("Request should be a post request")


def post_hashed_document(document, report, hospital_id, sc_endpoint):
    payload = {'reportId': report.report_id, 'hospitalId': hospital_id, 'documentHash': hashlib.sha256(document['document'].encode()).hexdigest()}
    response = requests.post(sc_endpoint+'/addHashToBlockchain', data=payload)
    if response.status_code == 200:
        return report.report_id
    elif response.status_code == 404:
        return response
    
def uploadDocument(document, visit, employee):
    # try:
    documentType = DocumentType.objects.filter(document_id=document['documentType']).first()
    report = Report(visit_id=visit, document=document['document'], created_employee=employee, updated_employee=employee, document_type=documentType)
    report.save()
    return post_hashed_document(document, report, HOSPITAL_ID, SMART_CONTRACT_ENDPOINT)
    # except:
      #  return -1

@csrf_exempt
def uploadDocumentBatch(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        print(body)
        visit = Visit.objects.filter(visit_id=body['visitId'])
        employee = Employee.objects.filter(employee_id=body['employeeId'])
        if visit.exists():
            if employee.exists():
                listOfDocuments = body['documents']
                reportIds = []
                for index, document in enumerate(listOfDocuments):
                    print('Inside')
                    if DocumentType.objects.filter(document_id=document['documentType']).exists():
                        id = uploadDocument(document, visit.first(), employee.first())
                        reportIds.append(id)
                    else:
                        reportIds.append(-1)
                print(reportIds)
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
        visit_id = request.GET.get('visit_id', -1)
        report_id = request.GET.get('report_id', -1)
        visit = Visit.objects.filter(visit_id=visit_id)
        report = Report.objects.filter(report_id=report_id)
        report_dict = {}
        if visit.exists():
            if report.exists():
                capsule, encrypted_document = get_encrypted_document(report.first().document, visit.first())
                report_dict['report_id'] = report_id
                report_dict['encrypted_document'] = base64.b64encode(encrypted_document).decode('utf-8')
                report_dict['capsule'] = base64.b64encode(bytes(capsule)).decode('utf-8')
                return JsonResponse(report_dict)
            return HttpResponseBadRequest("No Report exists with given ReportId")
        return HttpResponseBadRequest("No Visit exists with given VisitId")
    return HttpResponseBadRequest("Request should be a GET request")

@csrf_exempt
def get_documents(request):
    if request.method == 'GET':
        report_ids = request.GET.getlist('report_ids')
        response = []
        for report_id in report_ids:
            report_dict = {}
            report = Report.objects.filter(report_id=report_id)
            visit = report.first().visit_id
            visit = Visit.objects.filter(visit_id=visit.visit_id)
            if visit.exists():
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
            else :
                return HttpResponseBadRequest("No visit with this visitId exists")
        return JsonResponse({'result': response})
    return HttpResponseBadRequest("Request should be a get request")

def public_key_from_utf8(utf8_string: str) -> 'PublicKey':
    return PublicKey.from_bytes(base64.b64decode(utf8_string.encode('utf-8')))

def secret_key_from_utf8(utf8_string: str) -> 'SecretKey':
    return SecretKey.from_bytes(base64.b64decode(utf8_string.encode('utf-8')))


def get_hashed_document(sc_endpoint, report_id, hospital_id):
    payload = {'reportId': report_id, 'hospitalId': hospital_id}
    response = requests.post(sc_endpoint+'/getDocumentHash', data=payload)
    if response.status_code == 200:
        body = response.json()
        hashed_document = body['documentHash']
        return hashed_document
    elif response.status_code == 404:
        return response


@csrf_exempt
def add_documents(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        visitId = body['hospital_to_visit_id']
        visitQuerySet = Visit.objects.filter(visit_id=visitId)
        if visitQuerySet.exists():
            visit = visitQuerySet.first()
            status = []
            listOfDocuments = body['reports']
            for document in listOfDocuments:
                encryptedDocument = base64.b64decode(document['ciphertext'].encode('utf-8'))

                capsule_bytes = base64.b64decode(document['capsule'].encode('utf-8'))
                new_capsule = Capsule.from_bytes(capsule_bytes)

                hospital_report_unique_key=document['hospital_report_unique_key']
                key_list = hospital_report_unique_key.split("_")
                hospital_id = key_list[0]
                report_id = key_list[1]
                # accountAddress = document['address']
                patient_session_public_key = public_key_from_utf8(document['patient_session_public_key'])
                patient_session_verifying_key = public_key_from_utf8(document['patient_session_verifying_key'])
                # hospital_b_public_key = public_key_from_utf8(hospital_b_public_key_utf8)

                cfrag_bytes = base64.b64decode(document['cfrag'].encode('utf-8'))

                cfrag = CapsuleFrag.from_bytes(cfrag_bytes)
                cfrag = cfrag.verify(capsule = new_capsule,
                        verifying_pk=patient_session_verifying_key,
                                         delegating_pk=patient_session_public_key,
                                         receiving_pk=public_key_from_utf8(HOSPITAL_PUBLIC_KEY)
                                     # receiving_pk=hospital_b_public_key
                                    )


                cfrags = [cfrag]
                decrypted_document = decrypt_reencrypted(
                                                        secret_key_from_utf8(HOSPITAL_PRIVATE_KEY), 
                                                        patient_session_public_key, new_capsule, cfrags, encryptedDocument)
                # decrypted_document = decrypt_reencrypted(secret_key_from_utf8(hospital_b_secret_key_utf8), patient_session_public_key, new_capsule, cfrags, encryptedDocument)
                if hashlib.sha256(decrypted_document).hexdigest() == get_hashed_document(SMART_CONTRACT_ENDPOINT, report_id, hospital_id):
                # if True:
                    document_type = DocumentType(name="dummy")
                    document_type.save()
                    report = Report(visit_id=visit, document=decrypted_document, created_employee=visit.employee, updated_employee=visit.employee, document_type=document_type
                                    #  , hash_account_address="SampleAccountAddress", hash_index=3
                                    )
                # TODO will need to change document type to metadata passed by the patient, need to remove the hash fields from model and everywhere
                    report.save()
                    status.append({"report_id": document["report_id"], "status": 'Matched'})
                else:
                    status.append({"report_id": document["report_id"], "status": 'Did not match'})
            return JsonResponse({'status': status})
        return HttpResponseBadRequest('Specified VisitId does not exist')
    return HttpResponseBadRequest('Must be a POST request')

def publish_public_key(request):
    return HttpResponse(HOSPITAL_PUBLIC_KEY)

def home_page(request):
    return HttpResponse("You've reached Hospital "+ str(HOSPITAL_ID))