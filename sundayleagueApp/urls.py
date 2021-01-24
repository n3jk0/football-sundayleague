from django.urls import path
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

from . import views

app_name = 'sunday_league'

# todo: only one url for results and resultstext
urlpatterns = [
  path('', views.index, name='home'),
  url(r'^fixtures/(?P<league>[1-9]+)/$', views.fixtures, name='fixtures'),
  url(r'^standing/(?P<league>[1-9]+)/$', views.standing, name='standing'),
  url(r'^scorers/(?P<league>[1-9]+)/$', views.scorers, name='scorers'),
  url(r'^information/(?P<league>[1-9]+)/$', views.information, name='information'),
  url(r'^information/$', views.information, name='information'),
  url(r'^uploadfixtures/', views.uploadfixtures, name="upload-fixtures"),
  url(r'^results/(?P<file_id>.+)/$', views.results, name='results-by-id'),
  url(r'^resultstext/(?P<file_id>.+)/$', views.results_text, name='resultstext'),
  url(r'^fixturestext/(?P<file_id>.+)/$', views.fixtures_text, name='fixturestext'),
  path('table/', views.fill_table, name="fill-table"),
  url(r'^login/$', views.login_view, name='login')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
