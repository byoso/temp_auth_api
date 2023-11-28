from django.urls import path

from . import views

urlpatterns = [
    path('here/', views.here, name='here'),
]
