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
        'file_actions',
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
            return format_html("<a class=\"button\" href=\"/uploadfixtures/\" onclick='return confirm(\"Shranjevanje lahko traja nekaj časa. Ste prepričani da želite nadeljevati?\");'>Uvozi razpored</a>",)

    file_actions.short_description = "Uvozi datoteko"
