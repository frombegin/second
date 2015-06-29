from django.db import models
from django.conf import settings
from django.utils import timezone

from . import signals

import uuid
import os

# ------------------------------------------------------------------------------

def avatar_upload(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("avatars", filename)

# ------------------------------------------------------------------------------

class TeamManager(models.Manager):
    pass

class Team(models.Model):

    objects = TeamManager()

    name = models.CharField(max_length = 128)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=avatar_upload, blank=True)
    scope = models.IntegerField(default=1)
    public_visible = models.BooleanField(default=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="teams_created")
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("team_detail", args=[self.slug])

    @property
    def applicants(self):
        return self.memberships.filter(status=MembershipStatus.APPLIED)

    @property
    def invitees(self):
        return self.memberships.filter(status=MembershipStatus.INVITED)

    @property
    def declines(self):
        return self.memberships.filter(status=MembershipStatus.DECLINED)

    @property
    def rejections(self):
        return self.memberships.filter(status=MembershipStatus.REJECTED)

    @property
    def acceptances(self):
        return self.memberships.filter(status__in=[
            MembershipStatus.ACCEPTED,
            MembershipStatus.AUTO_JOINED]
        )

    @property
    def members(self):
        return self.acceptances.filter(role=MembershipRole.MEMBER)

    @property
    def managers(self):
        return self.acceptances.filter(role=MembershipRole.MANAGER)

    @property
    def owners(self):
        return self.acceptances.filter(role=MembershipRole.OWNER)

    def is_owner_or_manager(self, user):
        return self.acceptances.filter(
            role__in=[
                MembershipRole.OWNER,
                MembershipRole.MANAGER,
            ],
            user=user
        ).exists()

    def is_member(self, user):
        return self.members.filter(user=user).exists()

    def is_manager(self, user):
        return self.managers.filter(user=user).exists()

    def is_owner(self, user):
        return self.owners.filter(user=user).exists()

    def is_on_team(self, user):
        return self.acceptances.filter(user=user).exists()

    def add_user(self, user, role):
        status = MembershipStatus.INVITED
        membership, _ = self.memberships.get_or_create(
            user=user,
            defaults={"role": role, "status": status}
        )
        signals.added_member.send(sender=self, membership=membership)
        return membership

##    def invite_user(self, from_user, to_email, role, message=None):
##        if not JoinInvitation.objects.filter(signup_code__email=to_email).exists():
##            invite = JoinInvitation.invite(from_user, to_email, message, send=False)
##            membership, _ = self.memberships.get_or_create(
##                invite=invite,
##                defaults={"role": role, "status": MembershipStatus,INVITED}
##            )
##            invite.send_invite()
##            signals.invited_user.send(sender=self, membership=membership)
##            return membership


    def for_user(self, user):
        try:
            return self.memberships.get(user=user)
        except Membership.DoesNotExist:
            pass

    def status_for(self, user):
        membership = self.for_user(user=user)
        if membership:
            return membership.status

    def role_for(self, user):
        membership = self.for_user(user)
        if membership:
            return membership.role


class MembershipStatus(object):

    APPLIED = 0
    INVITED = 1
    DECLINED = 2
    REJECTED = 3
    ACCEPTED = 4
    AUTO_JOINED = 5

class MembershipRole(object):

    MEMBER = 0
    MANAGER = 1
    OWNER = 2

class Invitation(models.Model):
        
    created_at = models.DateTimeField(auto_now_add = True)

class Membership(models.Model):

    STATUS_CHOICES= [
        (MembershipStatus.APPLIED, "applied"),
        (MembershipStatus.INVITED, "invited"),
        (MembershipStatus.DECLINED, "declined"),
        (MembershipStatus.REJECTED, "rejected"),
        (MembershipStatus.ACCEPTED, "accepted"),
        (MembershipStatus.AUTO_JOINED, "auto joined")
    ]

    ROLE_CHOICES = [
        (MembershipRole.MEMBER, "member"),
        (MembershipRole.MANAGER, "manager"),
        (MembershipRole.OWNER, "owner")
    ]

    team = models.ForeignKey(Team, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="memberships", null=True, blank=True)
    invite = models.ForeignKey(Invitation, related_name="memberships", null=True, blank=True)
    role = models.IntegerField(default=MembershipRole.MEMBER, choices = ROLE_CHOICES)
    status = models.IntegerField(default=MembershipStatus.APPLIED, choices = STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add = True)


    def is_owner(self):
        return self.role == MembershipRole.ROLE_OWNER

    def is_manager(self):
        return self.role == MembershipRole.MANAGER

    def is_member(self):
        return self.role == MembershipRole.MEMBER

    def promote(self, by):
        role = self.team.role_for(by)
        if role in [MembershipRole.MANAGER, MembershipRole.OWNER]:
            if self.role == MembershipRole.MEMBER:
                self.role = MembershipRole.MANAGER
                self.save()
                signals.promoted_member.send(sender=self, membership=self)
                return True
        return False

    def demote(self, by):
        role = self.team.role_for(by)
        if role in [MembershipRole.MANAGER, MembershipRole.OWNER]:
            if self.role == MembershipRole.MANAGER:
                self.role = MembershipRole.MEMBER
                self.save()
                signals.demoted_member.send(sender=self, membership=self)
                return True
        return False

    def accept(self, by):
        role = self.team.role_for(by)
        if role in [MembershipRole.MANAGER, MembershipRole.OWNER]:
            if self.status == MembershipStatus.APPLIED:
                self.status = MembershipStatus.ACCEPTED
                self.save()
                signals.accepted_membership.send(sender=self, membership=self)
                return True
        return False

    def reject(self, by):
        role = self.team.role_for(by)
        if role in [Membership.ROLE_MANAGER, Membership.ROLE_OWNER]:
            if self.status == MembershipStatus.APPLIED:
                self.status = MembershipStatus.REJECTED
                self.save()
                signals.rejected_membership.send(sender=self, membership=self)
                return True
        return False

    def joined(self):
        self.user = self.invite.to_user
        if self.team.manager_access == Team.MANAGER_ACCESS_ADD:
            self.status = MembershipStatus.AUTO_JOINED
        else:
            self.status = MembershipStatus.INVITED
        self.save()

    def status(self):
        if self.user:
            return self.get_status_display()
        if self.invite:
            return self.invite.get_status_display()
        return "Unknown"

    def resend_invite(self):
        if self.invite is not None:
            code = self.invite.signup_code
            code.expiry = timezone.now() + datetime.timedelta(days=5)
            code.save()
            code.send()
            signals.resent_invite.send(sender=self, membership=self)

    def remove(self):
        if self.invite is not None:
            self.invite.signup_code.delete()
            self.invite.delete()
        self.delete()
        signals.removed_membership.send(sender=Membership, team=self.team, user=self.user)

    @property
    def invitee(self):
        return self.user or self.invite.to_user_email

    def __unicode__(self):
        return u"{0} in {1}".format(self.user, self.team)

    class Meta:
        unique_together = [("team", "user", "invite")]