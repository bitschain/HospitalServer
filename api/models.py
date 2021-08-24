from django.db import models

# Create your models here.
class UserSession(models.Model):
    sessionPublicKey = models.CharField(max_length = 512)
    patientId = models.IntegerField()
    visitId = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add = True)

def __str__(self):
    return self.sessionPublicKey
