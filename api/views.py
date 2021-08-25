from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Visit, mst_Patient
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