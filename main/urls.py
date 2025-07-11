from django.urls import path
from .views import *

urlpatterns = [
    path('', show_random_citation, name='show_random_citation'),
    path('add/', add_citation, name='add_citation'),
    path('top/', show_top_citations, name='show_top_citations'),
    path('vote/<int:citation_id>/', vote, name='vote'),
]