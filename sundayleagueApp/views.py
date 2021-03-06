from django.http import HttpResponse
from django.shortcuts import render
from sundayleagueApp.models import *
from sundayleagueApp.forms import *
from sundayleagueApp.services import SystemSettingsUtils
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import *
from django.contrib import messages
from django.template.defaulttags import register
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

import services.fixtures_service as FixturesServices
import services.results_service as ResultsService
from sundayleagueApp import constants
from django.shortcuts import redirect

import datetime
import logging

LEAGUE_PREFIX = 'league_'


# Create your views here.
def index(request):
    today = datetime.date.today()
    today_minus_3 = today - datetime.timedelta(days=3)
    # NOTE: this query works only on PostgresSQL
    # Show last results or next fixture by league
    round_to_show_by_league = Round.objects.filter(date__gt=today_minus_3).order_by('league_number', 'date').distinct('league_number').all()
    # Last results or next fixture wasn't found for at least one league. Get last round for that league
    if len(round_to_show_by_league) != 4:
        leagues_to_exclude = [r.league_number for r in round_to_show_by_league]
        # Append last round by missing leagues
        round_to_show_by_league |= Round.objects.exclude(league_number__in=leagues_to_exclude).order_by('league_number', '-date').distinct('league_number').all()
    rounds_group_by_league = {}
    [rounds_group_by_league.setdefault(LEAGUE_PREFIX + str(r.league_number), []).append(r) for r in
     round_to_show_by_league]

    all_matches = Match.objects.order_by("time").all()
    matches_group_by_rounds = {}
    [matches_group_by_rounds.setdefault(m.round_id, []).append(m) for m in all_matches]
    logging.info('Test')
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
            return redirect('sunday_league:home')
    return render(request, 'login.html', {'form': form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect('sunday_league:home')


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
                   'top_scorers': top_scorers, 'goals_by_match': goals_by_match,
                   'write_scorers_enabled': SystemSettingsUtils.get_bool_value(constants.WRITE_SCORERS_ENABLED)})


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


@require_GET
def information(request, league=1):
    last_information = Information.objects.order_by("-pk")
    last_information_text = last_information[0].info if last_information.exists() else ""
    return render(request, 'information.html', {'last_information': last_information_text, 'selected_league': league})


@require_GET
@login_required(login_url="/login/")
def dashboard(request):
    profile = request.user.profile
    user_team = profile.team
    editable_rounds = Round.objects.order_by('league_number', 'date').all() if profile.is_admin else Round.objects.filter(
        home_team=user_team).order_by('league_number', 'date').all()
    rounds_by_league = {}
    for round in editable_rounds:
        rounds_by_league.setdefault(round.league_number, []).append(round)
    completed_rounds = dict(zip(editable_rounds, [r.all_match_completed() for r in editable_rounds]))
    return render(request, 'dashboard.html', {'profile':profile, 'rounds': rounds_by_league, 'completed_rounds': completed_rounds})


@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def modify_matches(request, round_id=-1):
    round_id = int(round_id)
    profile = request.user.profile
    if round_id >= 0:
        if request.method == 'POST':
            if 'match_id' in request.POST:
                match_id = request.POST.get('match_id')
                match = Match.objects.get(id=match_id)
                form = MatchForm(profile, instance=match, data=request.POST)
            if form.is_valid():
                form.save()
                ResultsService.update_table()
                messages.success(request, "Rezultat je shranjen")
                return redirect('sunday_league:matches_by_round', round_id=round_id)
        try:
            selected_round = Round.objects.get(id=round_id)
            if not profile.is_admin and selected_round.home_team != profile.team:
                logging.warning("User: {} doesn't have privileges for round {}".format(profile.user, selected_round))
                return redirect('dashboard')
        except Round.DoesNotExist:
            logging.warning('Round with id ' + round_id + " doesn't exists")
            return redirect('dashboard')
        matches_for_round = Match.objects.filter(round=selected_round).order_by('time').all()
        forms = [MatchForm(profile, disabled=(not profile.is_admin and saving_disabled(m)), instance=m)for m in matches_for_round]

        return render(request, 'modify-matches.html',
                      {'profile': profile, 'selected_round': selected_round, 'matches': matches_for_round,
                       'write_scorers_enabled': SystemSettingsUtils.get_bool_value(constants.WRITE_SCORERS_ENABLED),
                       'forms': forms})


@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def upload_results(request, file_uuid=None):
    profile = request.user.profile
    if not profile.is_admin:
        return redirect('sunday_league:dashboard')

    if request.method == 'GET':
        form = FileForm()
        if file_uuid:
            form.instance = File.objects.get(uuid=file_uuid)
    elif request.method == 'POST':
        # Preview confirmed
        if 'file_id' in request.POST and request.POST.get('file_id'):
            file_id = request.POST.get('file_id')
            saved_matches = ResultsService.save_results_for_file(file_id)
            if not saved_matches:
                messages.warning(request, "Datoteka z id-jem {} ne obstaja!".format(file_id))
            else:
                messages.success(request, "{} rezultatov je bilo vnesenih.".format(len(saved_matches)))
                ResultsService.update_table()
                messages.success(request, "Lestvica je bila posodobljena.")
            return redirect('sunday_league:upload_results')

        # Genereate preview
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            file_id = file.id
            saved_results = ResultsService.preview_results_for_file(file_id)
            if not saved_results:
                messages.warning(request, "Datoteka z id-jem {} ne obstaja!".format(file_id))

            results_by_round = {}
            for result in saved_results:
                results_by_round.setdefault(result.round, []).append(result)
            # TODO: Delete file if cancel preview
            return render(request, 'upload-file.html', {"fixtures_upload": False, 'preview_matches': results_by_round, 'file_id': file_id})
        else:
            messages.warning(request, "Prišlo je do napake.")

    return render(request, 'upload-file.html', {'form': form, "fixtures_upload": False})


@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def upload_fixtures(request):
    profile = request.user.profile
    if not profile.is_admin:
        return redirect('sunday_league:dashboard')

    if request.method == 'GET':
        form = FileForm()
    elif request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            file.is_fixture = True
            file_id = file.id
            file.save()
            saved_results = FixturesServices.save_fixtures_for_file(file_id)
            if not saved_results:
                messages.warning(request, "Datoteka z id-jem {} ne obstaja!".format(file_id))
            else:
                ResultsService.update_table()
                messages.success(request, "Razpored je bil dodan.")
            return redirect('sunday_league:upload_fixtures')
        else:
            messages.warning(request, "Prišlo je do napake.")

    return render(request, 'upload-file.html', {'form': form, "fixtures_upload": True})


@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def modify_information(request, last):
    profile = request.user.profile
    if not profile.is_admin:
        return redirect('sunday_league:dashboard')

    if request.method == 'GET':
        form = InformationForm()
        if last:
            last_information = Information.objects.order_by("-pk").first()
            if not last_information:
                return redirect('sunday_league:modify_information')
            form = InformationForm(instance=last_information)
    elif request.method == 'POST':
        form = InformationForm(data=request.POST)
        if 'information_id' in request.POST and request.POST.get('information_id'):
            information_id = request.POST.get('information_id')
            information = Information.objects.get(id=information_id)
            form = InformationForm(instance=information, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Obvestilo je shranjeno.")
            return redirect('sunday_league:modify_last_information')

    return render(request, "modify-information.html", {"form": form, "last":last})


@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def player(request, player_id=-1):
    profile = request.user.profile
    if not profile.is_admin:
        return redirect('sunday_league:dashboard')

    if request.method == 'GET':
        form = PlayerForm()
        if int(player_id) > 0:
            form = PlayerForm(instance=Player.objects.get(id=player_id))

    elif request.method == 'POST':
        form = PlayerForm(data=request.POST)
        if int(player_id) > 0:
            player = Player.objects.get(id=player_id)
            form = PlayerForm(instance=player, data=request.POST)
        if form.is_valid():
            player = form.save()
            messages.success(request, "Igralec je shranjen.")
            return redirect('sunday_league:player', player_id=player.id)

    return render(request, "player.html", {"form": form})


@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def players(request):
    profile = request.user.profile
    if not profile.is_admin:
        return redirect('sunday_league:dashboard')

    players_by_league = {}
    for player in Player.objects.filter(team__isnull=False).order_by('-goals').all():
        # Use string for league due to django template restriction
        players_by_league.setdefault(str(player.team.league), []).append(player)

    if request.method == 'POST':
        for player in Player.objects.all():
            player_input_id = "player_" + str(player.id)
            player.goals = request.POST[player_input_id]
            player.save()
        return redirect('sunday_league:players')

    return render(request, "list_of_players.html", {"players_by_league": players_by_league})


@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def round(request, round_id=-1):
    profile = request.user.profile
    if not profile.is_admin:
        return redirect('sunday_league:dashboard')

    if request.method == 'GET':
        form = RoundForm()
        if int(round_id) > 0:
            form = RoundForm(instance=Round.objects.get(id=round_id))

    elif request.method == 'POST':
        form = RoundForm(data=request.POST)
        if int(round_id) > 0:
            round = Round.objects.get(id=round_id)
            form = RoundForm(instance=round, data=request.POST)
        if form.is_valid():
            round = form.save()
            messages.success(request, "Krog je shranjen.")
            return redirect('sunday_league:round', round_id=round.id)

    return render(request, "round.html", {"form": form})


@require_GET
@login_required(login_url="/login/")
def teams(request):
    profile = request.user.profile
    if not profile.is_admin:
        return redirect('sunday_league:dashboard')

    teams_by_league = {}
    for team in Team.objects.filter(league__gt=0).order_by('league', 'name').all():
        # Use string for league due to django template restriction
        teams_by_league.setdefault(str(team.league), []).append(team)
    return render(request, "list_of_teams.html", {"teams_by_league": teams_by_league})


@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def team(request, team_id=-1):
    profile = request.user.profile
    if not profile.is_admin:
        return redirect('sunday_league:dashboard')

    if request.method == 'GET':
        form = TeamForm()
        if int(team_id) > 0:
            form = TeamForm(instance=Team.objects.get(id=team_id))

    elif request.method == 'POST':
        form = TeamForm(data=request.POST)
        if int(team_id) > 0:
            team = Team.objects.get(id=team_id)
            form = TeamForm(instance=team, data=request.POST)
        if form.is_valid():
            team = form.save()
            messages.success(request, "Ekipa je shranjena.")
            return redirect('sunday_league:team', team_id=team.id)

    return render(request, "team.html", {"form": form})

# TODO: remove
# DEPRECATED: Method called from django admin
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


# TODO: remove
# DEPRECATED: Method called from django admin
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


@register.filter
def status_class(match):
    if match.status == match.MatchStatus.LIVE:
        return 'liveMatch'
    elif match.status == match.MatchStatus.COMPLETED:
        return 'endMatch'
    else:
        return 'confirmedMatch'


@register.filter
def saving_disabled(match):
    return match.status == match.MatchStatus.CONFIRMED

