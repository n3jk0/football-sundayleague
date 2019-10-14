from django.http import HttpResponse
from django.shortcuts import render
from sundayleagueApp.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import services.FixturesServices as FixturesServices
from collections import defaultdict


# Create your views here.
def index(request):
    return render(request, 'index.html')


def fixtures(request, league):
    if request.method == 'GET':
        # rounds = Round.objects.filter(league_number=league)
        all_rounds = Round.objects.all()
        rounds_group_by = defaultdict(list)
        [rounds_group_by[r.league_number].append(r) for r in all_rounds]
        print(rounds_group_by)
        matches = Match.objects.all()
        return render(request, 'fixtures.html', {'matches': matches})


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
