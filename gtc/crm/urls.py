from django.urls import path
from .views import contacts_all, contact

urlpatterns = [
    path('', contacts_all, name='contacts_all'),
    path('/<int:contact_id>', contact, name='contact'),
]
