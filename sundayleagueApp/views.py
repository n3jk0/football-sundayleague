from django.http import HttpResponse
from django.shortcuts import render
from sundayleagueApp.models import *
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.template.defaulttags import register
from django.core.paginator import Paginator

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
        all_rounds = Round.objects.filter(league_number=league).order_by('date')
        if selected_round is None:
            today = datetime.date.today()
            today_plus_4 = today + datetime.timedelta(days=4)
            last_round = all_rounds.order_by('date').filter(date__lte=today_plus_4).last()
            last_round_number = last_round.round_number if last_round else 1
            return redirect(request.path + "?round=" + str(last_round_number))
        filter_rounds = all_rounds
        if selected_round != 'all':
            if not selected_round:
                return redirect(request.path + "?round=all")
            elif int(selected_round) < 1:
                return redirect(request.path + "?round=1")

            filter_rounds = filter_rounds.filter(league_number=league, round_number=selected_round)

            if not filter_rounds.exists():
                return redirect(request.path + "?round=" + str(int(selected_round) - 1))
        rounds_group_by_league = {}
        [rounds_group_by_league.setdefault(LEAGUE_PREFIX + str(r.league_number), []).append(r) for r in filter_rounds]
        all_matches = Match.objects.order_by("time")
        if selected_team_id is not None:
            all_matches = all_matches.filter(Q(first_team_id=selected_team_id) | Q(second_team_id=selected_team_id))
        all_matches = all_matches.all()
        matches_group_by_rounds = {}
        [matches_group_by_rounds.setdefault(m.round_id, []).append(m) for m in all_matches]
        table_rows = TableRow.objects.filter(league=league).order_by('-points', 'match_played').all()
        top_scorers = Player.objects.filter(team__league=league, goals__gt=0).order_by('-goals')[:5]
        all_match_goals = MatchGoals.objects.filter(team__league=league).all()
        # todo: something better
        goals_by_match = {}
        [goals_by_match.setdefault(mg.match_id, []).append(mg) for mg in all_match_goals]
        for key, val in goals_by_match.items():
            goals_by_team = {}
            [goals_by_team.setdefault(mg.team_id, []).append(mg.scorer.name()) for mg in val]
            goals_by_match[key] = goals_by_team
        print(goals_by_match)

        return render(request, 'fixtures.html',
                      {'matches': matches_group_by_rounds, 'rounds': rounds_group_by_league, 'all_rounds': all_rounds,
                       'table_rows': table_rows, 'selected_round': selected_round, 'selected_league': league,
                       'top_scorers': top_scorers,
                       'goals_by_match': goals_by_match})
    else:
        return HttpResponse("Wrong method!", status=405)


def standing(request, league):
    if request.method == 'GET':
        table_rows = TableRow.objects.filter(league=league).order_by('-points', 'match_played').all()
        top_scorers = Player.objects.filter(team__league=league, goals__gt=0).order_by('-goals')[:5]
        return render(request, 'standing.html',
                      {'table_rows': table_rows, 'selected_league': league, 'top_scorers': top_scorers})
    else:
        return HttpResponse("Wrong method!", status=405)


def scorers(request, league):
    if request.method == 'GET':
        all_scorers = Player.objects.filter(team__league=league, goals__gt=0).order_by('-goals')
        scorers_paginator = Paginator(all_scorers, 10)
        page_number = request.GET.get('page')
        page_scorers = scorers_paginator.get_page(page_number)
        return render(request, 'scorers.html', {'selected_league': league, 'page_scorers': page_scorers})
    else:
        return HttpResponse("Wrong method!", status=405)


def information(request, league=1):
    if request.method == 'GET':
        last_information = Information.objects.order_by("-pk")
        last_information_text = last_information[0].info if last_information.exists() else ""
        return render(request, 'information.html', {'last_information': last_information_text, 'selected_league': league})
    else:
        return HttpResponse("Wrong method!", status=405)


@csrf_exempt
def uploadfixtures(request):
    # maybe not the best solution to allow GET method here
    if request.method == 'GET' or request.method == 'POST':
        if request.user.is_authenticated:
            FixturesServices.save_fixtures()
            ResultsService.fill_table()
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
def fixtures_text(request, file_id=-1):
    if request.method == 'GET':
        text = FixturesServices.get_fixtures_text()
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


@register.filter
def get_item(dictionary, key):
    print(dictionary, key)
    return dictionary.get(key)
