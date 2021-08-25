from typing import ValuesView
from django.urls import path
from . import views
import re
from django.conf.urls import url, include

urlpatterns = [
    path('create_session', views.createNewUserSession),
    path('generate_qr_string', views.generate_qr_string)
]