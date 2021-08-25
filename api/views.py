from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Visit, mst_Patient
import json

# Create your views here.

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
                latest_visit = Visit(session_public_key = body["publicKey"], patient_id = patient.first().patient_id)
                latest_visit.save()
            except Visit.DoesNotExist:
                return HttpResponse(status=404)
            proxy_server = 'dummy.com'
            #TODO: need to update this after discussion
            qr_string = proxy_server + "/" + latest_visit.session_public_key + "/" + latest_visit.visit_id
            return HttpResponse(qr_string)
        return HttpResponseBadRequest("Patient doesn't exist")
    return HttpResponseBadRequest("Request should be a post request")
