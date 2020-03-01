from django.urls import path
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from . import views

admin.autodiscover()

# todo: only one url for results and resultstext
urlpatterns = [
    path('', views.index, name='index'),
    url(r'^fixtures/(?P<league>[1-9]+)/$', views.fixtures, name='fixtures'),
    url(r'^standing/(?P<league>[1-9]+)/$', views.standing, name='standing'),
    path('teams/', views.teams, name="teams-all"),
    path('results/', views.results, name="all-results"),
    url(r'^results/(?P<file_id>.+)/$', views.results, name='results-by-id'),
    path('resultstext/', views.results_text, name="resultstext"),
    url(r'^resultstext/(?P<file_id>.+)/$', views.results_text, name='resultstext'),
    path('table/', views.fill_table, name="fill-table")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
