from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

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
	File = models.FileField()
	date_created = models.DateTimeField()
	date_modified = models.DateTimeField()