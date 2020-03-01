from django.http import HttpResponse
from django.shortcuts import render
from sundayleagueApp.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import services.FixturesServices as FixturesServices
import services.ResultsService as ResultsService
from django.shortcuts import redirect
import datetime

LEAGUE_PREFIX = 'league_'


# Create your views here.
def index(request):
    return fixtures(request, 1)


def fixtures(request, league):
    if request.method == 'GET':
        selected_round = request.GET.get('round', None)
        all_rounds = Round.objects.filter(league_number=league)
        if selected_round is None:
            today = datetime.date.today()
            today_plus_4 = today + datetime.timedelta(days=4)
            last_round = all_rounds.order_by('date').filter(date__lte=today_plus_4).last()
            return redirect(request.path + "?round=" + str(last_round.round_number))
        filter_rounds = all_rounds
        if selected_round != 'all':
            filter_rounds = filter_rounds.filter(league_number=league, round_number=selected_round)
        rounds_group_by_league = {}
        [rounds_group_by_league.setdefault(LEAGUE_PREFIX + str(r.league_number), []).append(r) for r in filter_rounds]
        all_matches = Match.objects.all().order_by("time")
        matches_group_by_rounds = {}
        [matches_group_by_rounds.setdefault(m.round_id, []).append(m) for m in all_matches]
        table_rows = TableRow.objects.filter(league=league).order_by('-points').all()
        return render(request, 'fixtures.html',
                      {'matches': matches_group_by_rounds, 'rounds': rounds_group_by_league, 'all_rounds': all_rounds,
                       'table_rows': table_rows, 'fixtures_class': 'btn-light', 'standing_class': 'btn-secondary',
                       'selected_round': selected_round, 'selected_league': league})
    else:
        return HttpResponse("Wrong method!", status=405)


def standing(request, league):
    if request.method == 'GET':
        table_rows = TableRow.objects.filter(league=league).order_by('-points').all()
        return render(request, 'standing.html',
                      {'table_rows': table_rows, 'fixtures_class': 'btn-secondary', 'standing_class': 'btn-light',
                       'selected_league': league})
    else:
        return HttpResponse("Wrong method!", status=405)


# todo: basic auth
# todo: call this commands from admin page
# todo: rename to fixtures
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

        return HttpResponse("DONE")
    else:
        return HttpResponse("Wrong method!", status=405)


@csrf_exempt
def results(request, file_id=-1):
    if request.method == 'POST':
        if int(file_id) > 0:
            saved_results = ResultsService.save_results_for_file(file_id)
            return HttpResponse("{} saved results for file: {}".format(len(saved_results), file_id))

        ResultsService.save_results()
        return HttpResponse("Save all results")
    else:
        return HttpResponse("Wrong method!", status=405)


@csrf_exempt
def results_text(request, file_id=-1):
    if request.method == 'GET':
        if int(file_id) > 0:
            text = ResultsService.get_results_text_by_id(file_id)
            return HttpResponse(text)

        text = ResultsService.get_results_text()
        return HttpResponse(text)
    else:
        return HttpResponse("Wrong method!", status=405)


@csrf_exempt
def fill_table(request):
    if request.method == 'POST':
        ResultsService.fill_table()
        return HttpResponse("DONE")
    else:
        return HttpResponse("Wrong method!", status=405)
