from django.contrib import admin
from django.utils.html import format_html

from .models import *
from .views import results
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
        'uuid',
        'is_fixture',
        'already_read',
        'file_content',
        'file_actions',
    )
    readonly_fields = (
        'id',
        'uuid',
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(r'^results/(?P<file_id>.+)/$', results, name='save_results_by_admin')
        ]
        return urls + custom_urls

    def file_actions(self, obj):
        disabled = ""
        if obj.already_read:
            disabled = "disabled"
        return format_html('<form action="/results/{}/" method="post"><button type="submit" class="button" {}>Uvozi</button></form>', obj.uuid, disabled)

    file_actions.short_description = "Uvozi datoteko"
