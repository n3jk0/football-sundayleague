from django.urls import path
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^fixtures/(?P<league>[1-9]+)/$', views.fixtures, name='fixtures'),
    path('teams/', views.teams, name="teams-all")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
