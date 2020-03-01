from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_exempt

from services import ResultsService
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
            url(r'^results/(?P<file_id>.+)/$', self.admin_site.admin_view(self.process_results_action),
                name='save_results_by_admin')
        ]
        return urls + custom_urls

    def file_actions(self, obj):
        print(obj)
        # todo: add href
        return format_html(
            '<form action="results/{}/" method="post"><button type="submit"class="button">Uvozi</button></form>'.format(obj.id)
        )
    file_actions.short_description = "Uvozi datoteko"

    @csrf_exempt
    def process_results_action(self, request, file_id, *args, **kwargs):
        print("lalalal")
        if request.method == 'POST':
            if int(file_id) > 0:
                saved_results = ResultsService.save_results_for_file(file_id)
                return HttpResponse("{} saved results for file: {}".format(len(saved_results), file_id))

            ResultsService.save_results()
            return HttpResponse("Save all results")
        else:
            return HttpResponse("Wrong method!", status=405)
