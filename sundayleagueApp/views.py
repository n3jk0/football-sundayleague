from django.http import HttpResponse
from django.shortcuts import render
from sundayleagueApp.models import *
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

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
        selected_team_id = request.GET.get('team_id', None)
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
        all_matches = Match.objects.order_by("time")
        if selected_team_id is not None:
            all_matches = all_matches.filter(Q(first_team_id=selected_team_id) | Q(second_team_id=selected_team_id))
        all_matches = all_matches.all()
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


@csrf_exempt
def uploadfixtures(request):
    # maybe not the best solution to allow GET method here
    if request.method == 'GET' or request.method == 'POST':
        if request.user.is_authenticated:
            saved_teams = FixturesServices.save_teams()
            messages.success(request, "{} ekip je bilo shranjenih.".format(len(saved_teams)))
            FixturesServices.save_rounds()
            FixturesServices.save_matches()
            messages.success(request, "Razpored je bil dodan.")
            response = redirect("/admin/sundayleagueApp/file/")
            response.status_code = 303
            return response
        else:
            return HttpResponse("Not authenticated", status=403)
    else:
        return HttpResponse("Wrong method!", status=405)


@csrf_exempt
def results(request, file_id=-1):
    # maybe not the best solution to allow GET method here
    if request.method == 'POST' or request.method == 'GET':
        if request.user.is_authenticated:
            if int(file_id) > 0:
                saved_results = ResultsService.save_results_for_file(file_id)
                messages.success(request, "{} rezultatov je bilo vnesenih.".format(len(saved_results)))
                ResultsService.fill_table()
                messages.success(request, "Lestvica je bila posodobljena.")
                response = redirect("/admin/sundayleagueApp/file/")
                response.status_code = 303
                return response

            ResultsService.save_results()
            print("Save all results")
            return redirect("/admin/sundayleagueApp/file/")
        else:
            return HttpResponse("Not authenticated", status=403)
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
