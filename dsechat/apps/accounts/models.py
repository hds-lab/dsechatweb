from django.db import models
from django.contrib.auth.models import AbstractUser

# class Participant(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL)
#     over18 = models.BooleanField()
#     gives_consent = models.BooleanField()

class User(AbstractUser):
    over18 = models.BooleanField(default=False)
    gives_consent = models.BooleanField(default=False)

