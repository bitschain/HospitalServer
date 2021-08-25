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
