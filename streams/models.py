from django.db import models

# Create your models here.
class Proxy(models.Model):
    endpoint = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    in_use = models.BooleanField(default=False)
    started_using = models.DateTimeField(auto_now=True)