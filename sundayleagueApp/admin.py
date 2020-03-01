from django.contrib import admin
from django.utils.html import format_html

from .views import results
from .models import *
from django.conf.urls import url

# Register your models here.

admin.site.register(Round)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(TableRow)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'is_fixture',
        'already_read',
        'file_content',
        'file_actions',
    )
    readonly_fields = (
        'id',
        'is_fixture',
        'already_read',
        'file_content',
        'file_actions',
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(r'^resultstext/(?P<file_id>.+)/$', results, name='resultstext-by-id')
        ]
        return urls + custom_urls

    def file_actions(self, obj):
        # todo: add href
        return format_html(
            '<a class="button" href="10">Uvozi</a>'
        )
    file_actions.short_description = "Uvozi datoteko"

    def process_results_action(self, request, file_id):
        if request.method != 'POST':
            raise NotImplementedError()
