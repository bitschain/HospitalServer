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
    path('get_documents', views.get_documents),
    path('add_documents', views.add_documents),
    path('public_key', views.publish_public_key),
    path('', views.home_page)
]