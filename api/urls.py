from django.urls import path
from . import views
import re
from django.conf.urls import url, include

urlpatterns = [
    path('create_session', views.createNewUserSession)
]