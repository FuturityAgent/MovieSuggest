"""MovieSuggest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from movie_suggestion import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('register/', views.SignUpView.as_view(), name='signup'),
    path('directors/', views.GetMyDirectorsView.as_view(), name='my-directors'),
    path('movies/last', views.AddLastMovieView.as_view(), name='last-movie'),
    path('movies/suggest', views.SuggestMovieView.as_view(), name='suggest-movie'),
    path('movies/<int:pk>/delete', views.DeleteMovieView.as_view(), name='delete-movie'),
    path('', views.IndexView.as_view(), name='home')
]

handler404 = "movie_suggestion.views.not_found_view"