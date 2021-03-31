from django.db import models
import jsonfield 
from django.db import models

class Contract(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    abi = jsonfield.JSONField()

class Collection(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

# Create your models here.
