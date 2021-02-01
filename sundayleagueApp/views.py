from django.http import HttpResponse
from django.shortcuts import render
from sundayleagueApp.models import *
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import *
from django.contrib import messages
from django.template.defaulttags import register
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

import services.FixturesService as FixturesServices
import services.ResultsService as ResultsService
from django.shortcuts import redirect

import datetime

LEAGUE_PREFIX = 'league_'


# Create your views here.
def index(request):
    today = datetime.date.today()
    today_minus_3 = today - datetime.timedelta(days=3)
    # NOTE: this query works only on PostgresSQL
    # Show last results or next fixture by league
    round_to_show_by_league = Round.objects.filter(date__gt=today_minus_3).order_by('league_number', 'date').distinct('league_number').all()
    if not round_to_show_by_league:
        # Last round by league
        round_to_show_by_league = Round.objects.order_by('league_number', '-date').distinct('league_number').all()
    rounds_group_by_league = {}
    [rounds_group_by_league.setdefault(LEAGUE_PREFIX + str(r.league_number), []).append(r) for r in round_to_show_by_league]

    all_matches = Match.objects.order_by("time").all()
    matches_group_by_rounds = {}
    [matches_group_by_rounds.setdefault(m.round_id, []).append(m) for m in all_matches]
    # TODO: goals by match
    return render(request, 'fixtures.html',
                  {'matches': matches_group_by_rounds, 'rounds': rounds_group_by_league, 'all_rounds': [],
                   'table_rows': [], 'selected_round': 0, 'selected_league': 1,
                   'top_scorers': [],
                   'goals_by_match': []})


def login_view(request):
    if request.method == 'GET':
        form = AuthenticationForm()
    elif request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            # TODO: redirect to result input page
            return redirect('sunday_league:home')
    return render(request, 'login.html', {'form': form})


@require_GET
def fixtures(request, league):
    selected_round = request.GET.get('round', None)
    selected_team_id = request.GET.get('team_id', None)
    all_rounds = Round.objects.filter(league_number=league).order_by('date')
    if not all_rounds:
        return redirect('sunday_league:home')
    if selected_round is None:
        today = datetime.date.today()
        today_minus_3 = today - datetime.timedelta(days=3)
        last_round = all_rounds.filter(date__gt=today_minus_3).first()
        last_round_number = last_round.round_number if last_round else all_rounds.last().round_number
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

    return render(request, 'fixtures.html',
                  {'matches': matches_group_by_rounds, 'rounds': rounds_group_by_league, 'all_rounds': all_rounds,
                   'table_rows': table_rows, 'selected_round': selected_round, 'selected_league': league,
                   'top_scorers': top_scorers,
                   'goals_by_match': goals_by_match})


@require_GET
def standing(request, league):
    table_rows = TableRow.objects.filter(league=league).order_by('-points', 'match_played').all()
    top_scorers = Player.objects.filter(team__league=league, goals__gt=0).order_by('-goals')[:5]
    return render(request, 'standing.html',
                  {'table_rows': table_rows, 'selected_league': league, 'top_scorers': top_scorers})


@require_GET
def scorers(request, league):
    all_scorers = Player.objects.filter(team__league=league, goals__gt=0).order_by('-goals')
    scorers_paginator = Paginator(all_scorers, 10)
    page_number = request.GET.get('page')
    page_scorers = scorers_paginator.get_page(page_number)
    return render(request, 'scorers.html', {'selected_league': league, 'page_scorers': page_scorers})


def information(request, league=1):
    last_information = Information.objects.order_by("-pk")
    last_information_text = last_information[0].info if last_information.exists() else ""
    return render(request, 'information.html', {'last_information': last_information_text, 'selected_league': league})


@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def uploadfixtures(request):
    # maybe not the best solution to allow GET method here
    if request.user.is_authenticated:
        FixturesServices.save_fixtures()
        ResultsService.update_table()
        messages.success(request, "Razpored je bil dodan.")
        response = redirect("/admin/sundayleagueApp/file/")
        response.status_code = 303
        return response
    else:
        return HttpResponse("Not authenticated", status=403)


@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def results(request, file_id=-1):
    # maybe not the best solution to allow GET method here
    if request.user.is_authenticated:
        if int(file_id) > 0:
            saved_results = ResultsService.save_results_for_file(file_id)
            if not saved_results:
                messages.warning(request, "Datoteka z id-jem {} ne obstaja!".format(file_id))
            else:
                messages.success(request, "{} rezultatov je bilo vnesenih.".format(len(saved_results)))
                ResultsService.update_table()
                messages.success(request, "Lestvica je bila posodobljena.")
            response = redirect("/admin/sundayleagueApp/file/")
            response.status_code = 303
            return response
        return redirect("/admin/sundayleagueApp/file/")
    else:
        return HttpResponse("Not authenticated", status=403)


@csrf_exempt
@require_GET
def results_text(request, file_id=-1):
    if int(file_id) > 0:
        text = ResultsService.get_results_text_by_id(file_id)
        return HttpResponse(text)

    text = ResultsService.get_results_text()
    return HttpResponse(text)


@csrf_exempt
@require_GET
def fixtures_text(request, file_id=-1):
    text = FixturesServices.get_fixtures_text()
    return HttpResponse(text)


@csrf_exempt
@require_POST
def fill_table(request):
    ResultsService.update_table()
    return HttpResponse("DONE")


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def next_round(all_rounds, current):
    if current == "all":
        return 'all'
    current_round = all_rounds.get(round_number=current)
    for i, r in enumerate(all_rounds):
        if r == current_round:
            next_round = all_rounds[i + 1] if i < len(all_rounds) - 1 else current_round
            break
    return next_round.round_number


@register.filter
def previous_round(all_rounds, current):
    if current == "all":
        return 'all'
    current_round = all_rounds.get(round_number=current)
    for i, r in enumerate(all_rounds):
        if r == current_round:
            previous_round = all_rounds[i - 1] if i > 0 else current_round
            break
    return previous_round.round_number