from django.forms import ModelForm
from .models import Movie


class LastMovieForm(ModelForm):
	"""Form to insert single movie record, with it's title and year of production"""
	class Meta:
		model = Movie
		fields = ['name', 'year_of_production']
