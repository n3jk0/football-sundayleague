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
  url(r'^results/(?P<file_id>.+)/$', views.results, name='results-by-id'),
  url(r'^resultstext/(?P<file_id>.+)/$', views.results_text, name='resultstext'),
  url(r'^fixturestext/(?P<file_id>.+)/$', views.fixtures_text, name='fixturestext'),
  url(r'^login/$', views.login_view, name='login'),
  url(r'^logout/$', views.logout_view, name='logout'),
  url(r'^dashboard/$', views.dashboard, name='dashboard'),
  url(r'^matches/(?P<round_id>\d+)/$', views.modify_matches, name='matches_by_round'),
  url(r'^uploadresults/$', views.upload_results, name='upload_results'),
  url(r'^uploadfixtures/$', views.upload_fixtures, name='upload_fixtures'),
  url(r'^modifyinformation/$', views.modify_information, {'last': False}, name='modify_information'),
  url(r'^modifyinformation/last$', views.modify_information, {'last': True}, name='modify_last_information'),
  url(r'^player/(?P<player_id>\d+)/$', views.player, name='player'),
  url(r'^player/$', views.player, name='player'),
  url(r'^players/$', views.players, name='players')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
