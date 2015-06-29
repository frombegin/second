#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.shortcuts import render
from django.views.generic import CreateView, ListView
from .models import Team, Membership
from .forms import TeamForm

class TeamCreateView(CreateView):

    model = Team
    form_class = TeamForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class TeamListView(ListView):

    model = Team