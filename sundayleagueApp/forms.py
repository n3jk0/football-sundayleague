from django import forms
from . import models
from fields import GroupedModelChoiceField


class MatchForm(forms.ModelForm):
    class Meta:
        model = models.Match
        fields = {'status', 'first_team_score', 'second_team_score'}

    def __init__(self, profile, disabled=False, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        if disabled:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = True
        elif not profile.is_admin:
            self.fields['status'].choices = [(models.Match.MatchStatus.LIVE.name, models.Match.MatchStatus.LIVE.label), (models.Match.MatchStatus.COMPLETED.name, models.Match.MatchStatus.COMPLETED.label)]


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = {'file_content'}


class InformationForm(forms.ModelForm):
    class Meta:
        model = models.Information
        fields = {'info'}


class PlayerForm(forms.ModelForm):
    team = GroupedModelChoiceField(queryset=models.Team.objects.order_by('league', 'name').all(), choices_groupby='league', groupby_prefix="Liga ")

    class Meta:
        model = models.Player
        fields = {'team', 'first_name', 'family_name', 'goals'}
