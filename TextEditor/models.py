from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from django.dispatch import receiver
import os

# Create your models here.
class MUser(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	activation_key = models.CharField(max_length=40)
	password_key = models.CharField(max_length=40)
	def natural_key(self): 
		return (self.user.first_name, self.user.id)	

class Document(models.Model):
	title = models.CharField(max_length=100)
	author = models.ForeignKey(MUser, on_delete=models.CASCADE)
	date_created = models.DateTimeField()
	date_modified = models.DateTimeField()

class CachedItem(models.Model):
	key = models.CharField(max_length=100)
	data_type = models.CharField(max_length=50)
	data_file = models.FileField()

@receiver(models.signals.post_delete, sender=CachedItem)
def auto_delete_file_on_delete(sender, instance, **kwargs):
	# source: http://stackoverflow.com/questions/16041232/django-delete-filefield
    if instance.data_file:
        if os.path.isfile(instance.data_file.path):
            os.remove(instance.data_file.path)