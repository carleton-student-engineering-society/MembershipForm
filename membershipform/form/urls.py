from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('signin', views.signin, name="signin"),
    path('callback', views.callback),
    path('home', views.home, name="home"),
    path('member_signup', views.member_signup, name="member_signup"),
    path('member_history', views.member_history, name="member_history"),
]