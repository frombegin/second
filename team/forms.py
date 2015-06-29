from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .models import Team, Membership

class TeamForm(forms.ModelForm):

    def clean_name(self):
        # if self.instance.pk is None and Team.objects.filter(slug=slug).exists():
        #     raise forms.ValidationError(_("Team with this name already exists"))
        if self.cleaned_data["name"].lower() in settings.TEAM_NAME_BLACKLIST:
            raise forms.ValidationError(_("You can not create a team by this name"))
        return self.cleaned_data["name"]

    class Meta:
        model = Team
        fields = [
            "name",
            "avatar",
            "description",
        ]