from django.http import HttpResponse
from django.shortcuts import render
from sundayleagueApp.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import services.FixturesServices as FixturesServices
import services.ResultsService as ResultsService
from collections import defaultdict

LEAGUE_PREFIX = 'league_'


# Create your views here.
def index(request):
    return fixtures(request, 1)


def fixtures(request, league):
    if request.method == 'GET':
        all_rounds = Round.objects.filter(league_number=league)
        rounds_group_by_league = {}
        [rounds_group_by_league.setdefault(LEAGUE_PREFIX + str(r.league_number), []).append(r) for r in all_rounds]
        all_matches = Match.objects.all().order_by("time")
        matches_group_by_rounds = {}
        [matches_group_by_rounds.setdefault(m.round_id, []).append(m) for m in all_matches]
        table_rows = TableRow.objects.filter(league=league).order_by('-points').all()
        return render(request, 'fixtures.html',
                      {'matches': matches_group_by_rounds, 'rounds': rounds_group_by_league, 'table_rows': table_rows})


# todo: basic auth
# todo: call this commands from admin page
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


@csrf_exempt
def results(request):
    if request.method == 'POST':
        ResultsService.get_results()
        return HttpResponse("DONE")


@csrf_exempt
def results_text(request):
    if request.method == 'GET':
        text = ResultsService.get_results_text()
        return HttpResponse(text)


@csrf_exempt
def fill_table(request):
    if request.method == 'POST':
        ResultsService.fill_table()
        return HttpResponse("DONE")
