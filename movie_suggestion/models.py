from django.db import models
from django.contrib.auth.models import User

class Person(models.Model):
	name = models.CharField(max_length=256)
	lastname = models.CharField(max_length=256)
	date_of_birth = models.DateField()
	nationality = models.CharField(max_length=128)
	imdb_id = models.CharField(max_length=20, default='')

	def __str__(self):
		return f"{self.name} {self.lastname} born {self.date_of_birth}"

	def __repr__(self):
		return f"{self.name} {self.lastname} born {self.date_of_birth}"

class Director(Person):
	no_of_oscars = models.IntegerField(default=0)


class Movie(models.Model):
	name = models.CharField(max_length=256)
	year_of_production = models.IntegerField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True)
	imdb_id = models.CharField(max_length=20, default='')
	genres = models.CharField(max_length=512, default='')
	keywords = models.CharField(max_length=512, default='')
