import imdb
import datetime
from collections import Counter
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
	template_name = 'index.html'
	login_url = '/login/'


class SignUpView(FormView):
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


class LogoutView(View):
	def get(self, request):
		logout(request)
		return redirect('home')


class AddLastMovieView(LoginRequiredMixin, FormView):
	form_class = LastMovieForm
	template_name = 'movies/last_movie.html'
	login_url = '/login/'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		last_seen_movies = Movie.objects.filter(user=self.request.user.id)
		context['movies'] = last_seen_movies
		return context

	def post(self, request, *args, **kwargs):
		form = LastMovieForm(request.POST)
		if form.is_valid():
			movie_title = form.cleaned_data.get('name')
			movie_year = form.cleaned_data.get('year_of_production')
			movie = Movie(name=movie_title, year_of_production=movie_year, user=request.user)
			movie_data = self.get_movie_data(movie)
			movie.imdb_id = movie_data.movieID
			movie.genres = ','.join(movie_data.data.get('genres', ' '))
			movie.keywords = ','.join(movie_data.get('keywords', ' '))
			director = self.get_movie_director(movie_data)
			movie.director = director
			movie.save()
			return redirect('last-movie')
		return redirect('last-movie')

	def get_movie_data(self, movie_obj: Movie):

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
			print(f"Director of movie {movie_rec.get('name')} not found")
			return
		except Exception as e:
			print(e)
			return


class SuggestMovieView(LoginRequiredMixin, TemplateView):
	login_url = '/login/'

	def get(self, request):
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
		filtered_movies = [m for m in best_matching_movies if m.movieID not in user_movies_ids and any([g in genres for g in m.get('genres')])]

		movies_to_suggest = [
			{
				'title': m.get('title'),
			 	'year': m.get('year'),
			 	'director': m.get('director', [{}])[0].get('name', 'unknown')
			}
			for m in filtered_movies
		]
		k_words = [k.replace('-', ' ') for k in top_common_keywords]
		return render(request, template_name='movies/suggestions.html', context={'movies': movies_to_suggest,
																				 'keywords': k_words})
		pdb.set_trace()
# Create your views here.
