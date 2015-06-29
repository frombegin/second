from django.contrib import admin
from .models import Team, Membership, Invitation

class TeamAdmin(admin.ModelAdmin):
    pass
admin.site.register(Team, TeamAdmin)

class MembershipAdmin(admin.ModelAdmin):
    pass
admin.site.register(Membership, MembershipAdmin)


class InvitationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Invitation, InvitationAdmin)
