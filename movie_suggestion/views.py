from collections import Counter
import datetime
import imdb
import time
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from .forms import LastMovieForm
from .models import Movie, Director

IMDB = imdb.IMDb()

valid_rec_types = ['movie', 'tv movie']


class IndexView(LoginRequiredMixin, TemplateView):
	"""Home page view. If user is not signed in, it will redirect him to the login page"""
	template_name = 'index.html'
	login_url = '/login/'


class SignUpView(FormView):
	"""Sign up view, where user can create an account"""
	form_class = UserCreationForm
	template_name = 'registration/signup.html'

	def post(self, request, *args, **kwargs):
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect('home')
		return render(request, template_name='registration/signup.html', context={'form': form})

class LogoutView(View):
	"""View used for logout from current account"""

	def get(self, request):
		logout(request)
		return redirect('home')


class AddLastMovieView(LoginRequiredMixin, FormView):
	"""View contains LastMovieForm, where user can add a single Movie record"""

	form_class = LastMovieForm
	template_name = 'movies/last_movie.html'
	login_url = '/login/'

	def get_context_data(self, **kwargs):
		"""Get context for the view, mostly Movie records, created by a current user
		:returns
		context - dict
		"""
		context = super().get_context_data(**kwargs)
		last_seen_movies = Movie.objects.filter(user=self.request.user.id)
		context['movies'] = last_seen_movies
		return context

	def post(self, request, *args, **kwargs):
		"""Add a Movie and a Director records to the database"""
		form = LastMovieForm(request.POST)
		if form.is_valid():
			movie_title = form.cleaned_data.get('name')
			movie_year = form.cleaned_data.get('year_of_production')
			movie = Movie(name=movie_title, year_of_production=movie_year, user=request.user)
			movie_data = self.get_movie_data(movie)
			if not movie_data:
				context = self.get_context_data()
				context['form'] = LastMovieForm()
				context['errors'] = [f"Movie {movie_title} released in the year {movie_year} doesn't exist :("]
				return render(request, 'movies/last_movie.html', context=context)
			movie.name = movie_data.data.get('title')
			movie.imdb_id = movie_data.movieID
			movie.genres = ','.join(movie_data.data.get('genres', ' '))
			movie.keywords = ','.join(movie_data.get('keywords', ' '))
			director = self.get_movie_director(movie_data)
			if director:
				movie.director = director
			movie.save()
			return redirect('last-movie')
		return redirect('last-movie')

	def get_movie_data(self, movie_obj: Movie):
		"""Gets detailed data about movie from IMDb database,
		obtains keywords for movie with specific IMDb id"""

		movies = IMDB.search_movie(movie_obj.name)
		movies = [rec for rec in movies if rec.get('year', 0) == movie_obj.year_of_production \
				  and rec.get('kind') in valid_rec_types]

		if not movies:
			return None
		match_movie = movies[0]
		movie_rec = IMDB.get_movie(match_movie.movieID)
		movie_rec['keywords'] = IMDB.get_movie(match_movie.movieID, info='keywords').data.get('keywords')
		return movie_rec

	def get_movie_director(self, movie_rec):
		"""Gets a detailed data about movie director, creates a single
		Director record in the database
		:returns
		director_obj - Director
		"""
		try:
			director = movie_rec.get('director')
			director = director[0]
			#if director already exists in the database, stop and return existing record
			director_records = Director.objects.filter(imdb_id=director.personID)
			if director_records and director_records[0].imdb_id != '':
				return director_records[0]
			elif director_records and director_records[0].imdb_id == '':
				return None

			director_data = IMDB.get_person(director.personID)
			director_name = director_data.get('name', '').split(' ')[0]
			director_lastname = director_data.get('name', '').split(' ')[-1]
			director_birthday = director_data.get('birth date', '')
			director_birthday = datetime.datetime.strptime(director_birthday, "%Y-%m-%d").date()
			director_object = Director(name=director_name,
									   lastname=director_lastname,
									   date_of_birth=director_birthday, imdb_id= director.personID)

			director_object.save()
			return director_object
		except IndexError:
			print(f"Director of movie {movie_rec.get('name')} not found")
			return
		except Exception as e:
			print(e)
			return


class SuggestMovieView(LoginRequiredMixin, TemplateView):
	"""View to show movies recommended for current user"""
	login_url = '/login/'

	def get(self, request, *args, **kwargs):
		"""Based on last 3 Movie records inserted to the database by an user, creates a list of
		5 most common keywords then for each keywords gets a list of movies matching this keyword,
		concatenates all lists together and gets 10 most common positions.
		:returns
		render function
		"""
		start = time.time()
		user_movies = Movie.objects.filter(user=request.user.id)
		user_movies_ids = list(user_movies.values_list('imdb_id', flat=True))
		last_movies = user_movies.order_by('-id')[:3]
		genres = []
		keywords = Counter()
		for line in last_movies:
			genres += line.genres.split(',')
			keywords += Counter(line.keywords.split(','))

		genres = list(set(genres))
		top_common_keywords = [k[0] for k in keywords.most_common(5)]
		potential_movies = [IMDB.get_keyword(k_word) for k_word in top_common_keywords]
		potential_movies = Counter([m for m_list in potential_movies for m in m_list if m.get('kind') in valid_rec_types])
		best_matching_movies = [IMDB.get_movie(m[0].movieID) for m in potential_movies.most_common(10)]
		filtered_movies = [m for m in best_matching_movies if m.movieID not in user_movies_ids and\
							any([g in genres for g in m.get('genres')])]

		movies_to_suggest = [
			{
				'title': m.get('title'),
				'year': m.get('year'),
				'director': m.get('director', [{}])[0].get('name', 'unknown')
			}
		for m in filtered_movies
		]
		k_words = [k.replace('-', ' ') for k in top_common_keywords]
		print("ZNALEZIENIE FILMÓW DO POLECENIA ZAJĘŁO: " + str(time.time() - start) + " sekund")
		return render(request, template_name='movies/suggestions.html', context={
			'movies': movies_to_suggest,
			'keywords': k_words})


class GetMyDirectorsView(LoginRequiredMixin, TemplateView):
	login_url = '/login/'

	def get(self, request, *args, **kwargs):
		user_movies = Movie.objects.filter(user=request.user.id)
		directors = Counter([movie.director for movie in user_movies if movie.director])
		directors = [{'name': person[0], 'no_of_movies': person[1]} for person in directors.most_common()]
		return render(request, 'directors/top_directors.html', context={'directors': directors})
# Create your views here.
