from django.urls import path
from .views import read_all, create, update, delete

urlpatterns = [
    path('all/', read_all, name='read_all'),
    path('new/', create, name='create'),
    path('update/<int:id>', update, name='update'),
    path('delete/<int:id>', delete, name='delete')
]
