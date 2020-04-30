from django.urls import path

from acts_creator import views


urlpatterns = [
    path('', views.main_page, name='main_page'),
]
