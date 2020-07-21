from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from .forms import LastMovieForm
from .models import Movie, Director
import imdb
import datetime
import pdb

IMDB = imdb.IMDb()

class IndexView(LoginRequiredMixin, TemplateView):
	template_name = 'index.html'
	login_url = '/login/'


class SignUpView(FormView):
	form_class = UserCreationForm
	template_name = 'registration/signup.html'

	def post(self, request, *args, **kwargs):
		# pdb.set_trace()
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect('home')


class LogoutView(View):
	def get(self, request):
		logout(request)
		return redirect('home')


class AddLastMovieView(FormView):
	form_class = LastMovieForm
	template_name = 'movies/last_movie.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		last_seen_movies = Movie.objects.filter(user=self.request.user.id)
		context['movies'] = last_seen_movies
		return context

	def post(self, request, *args, **kwargs):
		form = LastMovieForm(request.POST)
		# pdb.set_trace()
		if form.is_valid():
			# form.save()
			movie_title = form.cleaned_data.get('name')
			movie_year = form.cleaned_data.get('year_of_production')
			movie = Movie(name=movie_title, year_of_production=movie_year, user=request.user)
			# movie.save()
			movie_data = self.get_movie_data(movie)
			movie.imdb_id = movie_data.movieID
			pdb.set_trace()
			movie.genres = ','.join(movie_data.data.get('genres', ' '))
			movie.keywords = ','.join(movie_data.get('keywords', ' '))
			director = self.get_movie_director(movie_data)
			movie.director = director
			movie.save()
			return redirect('last_movie')
		return redirect('last_movie')

	def get_movie_data(self, movie_obj: Movie):
		valid_rec_types = ['movie', 'tv movie']
		movies = IMDB.search_movie(movie_obj.name)
		movies = [rec for rec in movies if rec.get('year', 0) == movie_obj.year_of_production \
				  and rec.get('kind') in valid_rec_types]

		if not movies:
			return
		match_movie = movies[0]
		movie_rec = IMDB.get_movie(match_movie.movieID)
		movie_rec['keywords'] = IMDB.get_movie(match_movie.movieID, info='keywords').data.get('keywords')
		return movie_rec

	def get_movie_director(self, movie_rec):
		try:
			director = movie_rec.get('director')
			director = director[0]
			director_data = IMDB.get_person(director.personID)
			# pdb.set_trace()
			director_name = director_data.get('name', '').split(' ')[0]
			director_lastname = director_data.get('name', '').split(' ')[-1]
			director_birthday = director_data.get('birth date', '')
			director_birthday = datetime.datetime.strptime(director_birthday, "%Y-%m-%d").date()
			director_object = Director(name=director_name,
									   lastname=director_lastname,
									   date_of_birth=director_birthday)

			director_object.save()
			return director_object
		except IndexError:
			print("Director of movie {movie.get('name')} not found")
			return
		except Exception as e:
			print(e)
			return

class SuggestMovieView(View):
	def get(self, request):
		last_movies = Movie.objects.filter(user=request.user.id).order_by('-id')[:3]



# Create your views here.
