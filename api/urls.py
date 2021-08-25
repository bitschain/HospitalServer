from typing import ValuesView
from django.urls import path
from . import views
import re
from django.conf.urls import url, include

urlpatterns = [
    path('create_session', views.createNewUserSession),
    path('generate_qr_string', views.generate_qr_string),
    path('upload_documents', views.uploadDocumentBatch),
    path('download_document', views.download_document),
    path('send_encrypted_doc', views.send_encrypted_documents_to_proxy),
]