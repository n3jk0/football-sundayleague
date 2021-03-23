from django import forms
from .custom_widgets import DataListWidget
from . import models
from .fields import GroupedModelChoiceField


class MatchForm(forms.ModelForm):
    first_team_scorers=forms.CharField(max_length=200)
    second_team_scorers=forms.CharField(max_length=200)

    class Meta:
        model = models.Match
        fields = {'status', 'first_team_score', 'second_team_score'}

    def __init__(self, profile, disabled=False, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        first_team_scorers_list = map((lambda player: player.name()), models.Player.objects.filter(team=self.instance.first_team).all())
        second_team_scorers_list = map((lambda player: player.name()), models.Player.objects.filter(team=self.instance.second_team).all())
        self.fields['first_team_scorers'].widget = DataListWidget(data_list=first_team_scorers_list, name='first_team_scorers')
        self.fields['second_team_scorers'].widget = DataListWidget(data_list=second_team_scorers_list, name='second_team_scorers')
        if disabled:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = True
        elif not profile.is_admin:
            self.fields['status'].choices = [(models.Match.MatchStatus.LIVE.name, models.Match.MatchStatus.LIVE.label), (models.Match.MatchStatus.COMPLETED.name, models.Match.MatchStatus.COMPLETED.label)]

    def save(self, commit=True):
        # TODO: first_team_scorers and second_team_scorers
        # self.cleaned_data['first_team_scorers']
        return super(MatchForm, self).save(commit=commit)


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
