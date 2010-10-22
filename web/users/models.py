from django.db import models
from django.contrib import admin

class User(models.Model):
	username = models.CharField(max_length = 200)
	password = models.CharField(max_length = 200)
	email    = models.CharField(max_length = 200)
   	registration_date = models.DateTimeField('date')
	
	def __unicode__(self):
		return self.title
		
	def __str__(self):
		return self.title
		
admin.site.register(User)
		