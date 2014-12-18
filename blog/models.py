from django.db import models

class Post(models.Model):
	title = models.CharField(max_length=200)
	created_date = models.DateTimeField()
	content = models.TextField()