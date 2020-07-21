from django.forms import fields, ModelForm
from .models import Movie


class LastMovieForm(ModelForm):
	class Meta:
		model = Movie
		fields = ['name', 'year_of_production']
