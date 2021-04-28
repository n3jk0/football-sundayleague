from django import forms
from django.db.models import Q, CharField, Value
from django.db.models.functions import Concat
from .custom_widgets import DataListWidget
from . import models
from .fields import GroupedModelChoiceField
from sundayleagueApp.services import SystemSettingsUtils
from sundayleagueApp import constants


class MatchForm(forms.ModelForm):
    first_team_scorers_count_field = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    second_team_scorers_count_field = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    class Meta:
        model = models.Match
        fields = {'status', 'first_team_score', 'second_team_score'}

    def __init__(self, profile, disabled=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_team_scorers_count = 0
        self.second_team_scorers_count = 0
        self.match_id = self.instance.id

        if (SystemSettingsUtils.get_bool_value(constants.WRITE_SCORERS_ENABLED)):
            if self.data:
                pass
            else:
                first_team_scorers_count_field_name = str(self.match_id) + '_first_team_scorers_count'
                second_team_scorers_count_field_name = str(self.match_id) + '_second_team_scorers_count'

                self.fields['first_team_scorers_count_field'].widget.attrs['id'] = first_team_scorers_count_field_name
                self.fields['second_team_scorers_count_field'].widget.attrs['id'] = second_team_scorers_count_field_name

                goals_by_match = models.MatchGoals.objects.filter(match=self.instance)
                first_team_goals = goals_by_match.filter(Q(team=self.instance.first_team) | Q(team__isnull=True)).all()
                second_team_goals = goals_by_match.filter(Q(team=self.instance.second_team) | Q(team__isnull=True)).all()

                for goalData in first_team_goals:
                    self.add_new_first_team_scorer_field(goalData)

                for goalData in second_team_goals:
                    self.add_new_second_team_scorer_field(goalData)

                # Set empty input
                self.add_new_first_team_scorer_field()
                self.add_new_second_team_scorer_field()

                self.fields['first_team_scorers_count_field'].initial = self.first_team_scorers_count
                self.fields['second_team_scorers_count_field'].initial = self.second_team_scorers_count

        if disabled:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = True
        elif not profile.is_admin:
            self.fields['status'].choices = [(models.Match.MatchStatus.LIVE.name, models.Match.MatchStatus.LIVE.label), (models.Match.MatchStatus.COMPLETED.name, models.Match.MatchStatus.COMPLETED.label)]


    def get_first_team_scorers_fields(self):
        for field_name in self.fields:
            if 'first_team_scorer' in field_name and 'count' not in field_name:
                yield self[field_name]

    def get_second_team_scorers_fields(self):
        for field_name in self.fields:
            if 'second_team_scorer' in field_name and 'count' not in field_name:
                yield self[field_name]

    def add_new_first_team_scorer_field(self, goal=None):
        first_team_scorers_list = map((lambda player: player.name()), models.Player.objects.filter(team=self.instance.first_team).all())
        first_team_field_name = str(self.match_id) + '_first_team_scorer_' + str(self.first_team_scorers_count)
        self.fields[first_team_field_name] = forms.CharField(max_length=200, required=False)
        self.fields[first_team_field_name].widget = DataListWidget(data_list=first_team_scorers_list, name=first_team_field_name)
        self.first_team_scorers_count += 1
        if goal:
            self.fields[first_team_field_name].initial = goal.scorer.name()
        return self[first_team_field_name]

    def add_new_second_team_scorer_field(self, goal=None):
        second_team_scorers_list = map((lambda player: player.name()), models.Player.objects.filter(team=self.instance.second_team).all())
        second_team_field_name = str(self.match_id) + '_second_team_scorer_' + str(self.second_team_scorers_count)
        self.fields[second_team_field_name] = forms.CharField(max_length=200, required=False)
        self.fields[second_team_field_name].widget = DataListWidget(data_list=second_team_scorers_list, name=second_team_field_name)
        self.second_team_scorers_count += 1
        if goal:
            self.fields[second_team_field_name].initial = goal.scorer.name()
        return self[second_team_field_name]


    def save(self, commit=True):
        match = self.instance
        first_team_goals = match.matchgoals_set.all().delete()
        players = models.Player.objects.annotate(name=Concat('first_name', Value(' '), 'family_name', output_field=CharField()))

        for field_name in self.data:
            if 'first_team_scorer' in field_name and 'count' not in field_name and self.data[field_name]:
                player_name = self.data[field_name]
                player = self.get_or_create_player(player_name, players)
                goal = models.MatchGoals.objects.create(match=match, team=match.first_team,scorer=player)
                print(goal,  "saved!")
            if 'second_team_scorer' in field_name and 'count' not in field_name and self.data[field_name]:
                player_name = self.data[field_name]
                player = self.get_or_create_player(player_name, players)
                goal = models.MatchGoals.objects.create(match=match, team=match.second_team,scorer=player)
                print(goal,  "saved!")

        return super(MatchForm, self).save(commit=commit)

    def get_or_create_player(self, player_name, players):
        # Maybe better with .exists() check?
        try:
            player = players.get(name=player_name)
        except models.Player.DoesNotExist:
            # TODO: Players with more then one name
            splited_name = player_name.split(" ")
            player = models.Player.objects.create(first_name=splited_name[0], family_name=splited_name[1])
        return player


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = {'file_content'}


class InformationForm(forms.ModelForm):
    class Meta:
        model = models.Information
        fields = {'info'}

    def __init__(self, *args, **kwargs):
        super(InformationForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.id is not None:
            replaced_info = self.instance.info.replace("<br/>", "\n")
            self.instance.info = replaced_info
            self.initial['info'] = replaced_info


    def save(self, commit=True):
        # self.cleaned_data['first_team_scorers']
        if self.instance and self.instance.id is not None:
            self.instance.info = self.instance.info.replace("\n", "<br/>")
        return super(InformationForm, self).save(commit=commit)


class PlayerForm(forms.ModelForm):
    team = GroupedModelChoiceField(queryset=models.Team.objects.order_by('league', 'name').all(), choices_groupby='league', groupby_prefix="Liga ")

    class Meta:
        model = models.Player
        fields = {'team', 'first_name', 'family_name', 'goals'}


class RoundForm(forms.ModelForm):
    home_team = GroupedModelChoiceField(queryset=models.Team.objects.order_by('league', 'name').all(), choices_groupby='league', groupby_prefix="Liga ")
    date = forms.DateField(input_formats=['%d.%m.%Y'], widget=forms.DateInput(format='%d.%m.%Y'))

    class Meta:
        model = models.Round
        fields = '__all__'


class TeamForm(forms.ModelForm):
    class Meta:
        model = models.Team
        fields = '__all__'
