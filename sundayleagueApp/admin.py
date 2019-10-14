from django.contrib import admin

from .models import Round, Team, Match, File

# Register your models here.

admin.site.register(Round)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(File)
