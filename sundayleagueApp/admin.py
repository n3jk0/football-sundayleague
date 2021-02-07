from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User, Group

from .models import *
from .views import results
import services.ResultsService as ResultsService
from django.conf.urls import url


class MyAdminSite(admin.AdminSite):
    login_template = 'admin/login.html'


class InformationAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')


class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')

    # def save_model(self, request, obj, form, change):
    #     obj.save()
    #     ResultsService.update_table()


class FileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'uuid',
        'is_fixture',
        'already_read',
        'file_content',
        'file_actions',
    )
    readonly_fields = (
        'id',
        'uuid',
        'file_actions',
        'text_content'
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(r'^results/(?P<file_id>.+)/$', results, name='save_results_by_admin')
        ]
        return urls + custom_urls

    def file_actions(self, obj):
        if not obj.is_fixture:
            if obj.already_read or obj.id is None:
                # disabled button
                return format_html("<a class=\"button\" disabled>Uvozi rezultate</a>")
            return format_html("<a class=\"button\" href=\"/results/{}/\" >Uvozi razultate</a>", obj.id)
        else:
            if obj.already_read or obj.id is None:
                # disabled button
                return format_html("<a class=\"button\" disabled>Uvozi razpored</a>")
            return format_html(
                "<a class=\"button\" href=\"/uploadfixtures/{}/\" onclick='return confirm(\"Shranjevanje lahko traja nekaj časa. Ste prepričani da želite nadeljevati?\");'>Uvozi razpored</a>", obj.id)

    file_actions.short_description = "Uvozi datoteko"


# Register your models here.
site = MyAdminSite(name='admin')

site.register(User)
site.register(Group)
site.register(Profile)

site.register(Round)
site.register(Team)
site.register(TableRow)

site.register(Player)
site.register(MatchGoals)

site.register(Information, InformationAdmin)
site.register(Match, MatchAdmin)
site.register(File, FileAdmin)
