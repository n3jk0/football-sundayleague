from django.http import HttpResponse
from django.shortcuts import render
from sundayleagueApp.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import services.FixturesServices as FixturesServices


# Create your views here.
def index(request):
    return render(request, 'index.html')


def fixtures(request, league):
    if request.method == 'GET':
        print(league)
        # matches = Match.objects.all().filter()
        return render(request, 'fixtures.html')


@csrf_exempt
def teams(request):
    if request.method == 'GET':
        all_teams = Team.objects.all()
        teams_json = {}
        for i, team in enumerate(all_teams):
            teams_json[i] = team.name
        return JsonResponse(teams_json)
    elif request.method == 'POST':
        print("I'm in")
        FixturesServices.save_teams()
        FixturesServices.save_rounds()
        FixturesServices.save_matches()

        # todo: redirect to get
        return HttpResponse("DONE")
    else:
        return HttpResponse("Wrong method!")
