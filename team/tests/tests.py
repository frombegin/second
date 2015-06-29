from django.test import TestCase
from django.contrib.auth.models import User
from team.models import Team, Membership, avatar_upload, MembershipRole, MembershipStatus

# import teams.receivers  # noqa - for django 1.6 tests


class BaseTeamTests(TestCase):

    def _create_team(self):
        return Team.objects.create(
            name="xxxz",
            creator=self.user,
        )

    def setUp(self):
        self.user = User.objects.create_user(username="baohua")


class AvatarUploadTests(TestCase):

    def test_avatar_upload_filename(self):
        path = avatar_upload(None, "MyHeadshot.png")
        self.assertTrue(path.startswith("avatars"))
        self.assertTrue(path.endswith(".png"))


class TeamTests(BaseTeamTests):

    def test_team_creation(self):
        team = self._create_team()
        self.assertEquals(team.name, "xxxz")
        self.assertEquals(team.creator, self.user)

    def test_team_absolute_url(self):
        team = self._create_team()
        self.assertTrue(team.pk in team.get_absolute_url())

    def test_team_str(self):
        team = self._create_team()
        self.assertEquals(str(team), "xxxz")

    def test_team_creation_owner_is_member(self):
        team = self._create_team()
        team_user = team.memberships.all()[0]
        self.assertEquals(str(team_user), "baohua in xxxz")

    def test_team_role_for(self):
        team = self._create_team()
        self.assertEquals(team.role_for(self.user), MembershipRole.OWNER)

    def test_unknown_user(self):
        team = self._create_team()
        other_user = User.objects.create_user(username="paltman")
        self.assertIsNone(team.for_user(other_user))
        self.assertIsNone(team.role_for(other_user))

    def test_user_is_member(self):
        team = self._create_team()
        other_user = User.objects.create_user(username="paltman")
        team.add_user(other_user, MembershipRole.MEMBER)
        self.assertTrue(team.is_on_team(other_user))

    def test_member_can_leave(self):
        team = self._create_team()
        other_user = User.objects.create_user(username="paltman")
        team.add_user(other_user, MembershipRole.MEMBER)
        self.assertTrue(team.can_leave(other_user))

    def test_manager_cannot_leave(self):
        team = self._create_team()
        self.assertFalse(team.can_leave(self.user))

    def test_owner_is_member(self):
        team = self._create_team()
        self.assertTrue(team.is_on_team(self.user))


class ManagerAddMemberOpenTests(BaseTeamTests):


    def test_cannot_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        team.add_user(paltman, MembershipRole.MEMBER)
        self.assertFalse(team.can_apply(paltman))

    def test_can_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertFalse(team.can_apply(paltman))

    def test_can_join_non_member(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertTrue(team.can_join(paltman))

    def test_can_join_invited(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        membership = team.add_user(paltman, MembershipRole.MEMBER)
        membership.status = MembershipStatus.INVITED
        membership.save()
        self.assertTrue(team.can_join(User.objects.get(username="paltman")))

    def test_can_join_declined(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        team.add_user(paltman, MembershipStatus.DECLINED)
        self.assertFalse(team.can_join(paltman))


class ManagerAddMemberApplicationTests(BaseTeamTests):


    def test_cannot_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        team.add_user(paltman, MembershipRole.MEMBER)
        self.assertFalse(team.can_apply(paltman))

    def test_can_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertTrue(team.can_apply(paltman))

    def test_can_join_non_member(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertFalse(team.can_join(paltman))

    def test_can_join_invited(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        membership = team.add_user(paltman, MembershipRole.MEMBER)
        membership.status = MembershipStatus.INVITED
        membership.save()
        self.assertTrue(team.can_join(User.objects.get(username="paltman")))

    def test_can_join_declined(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        team.add_user(paltman, MembershipStatus.DECLINED)
        self.assertFalse(team.can_join(paltman))


class ManagerAddMemberInvitationTests(BaseTeamTests):

    def test_cannot_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        team.add_user(paltman, MembershipRole.MEMBER)
        self.assertFalse(team.can_apply(paltman))

    def test_can_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertFalse(team.can_apply(paltman))

    def test_can_join_non_member(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertFalse(team.can_join(paltman))

    def test_can_join_invited(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        membership = team.add_user(paltman, MembershipRole.MEMBER)
        membership.status = MembershipStatus.INVITED
        membership.save()
        self.assertTrue(team.can_join(User.objects.get(username="paltman")))

    def test_can_join_declined(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        team.add_user(paltman, MembershipStatus.DECLINED)
        self.assertFalse(team.can_join(paltman))


class ManagerInviteMemberOpenTests(BaseTeamTests):

    def test_cannot_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        team.add_user(paltman, MembershipRole.MEMBER)
        self.assertFalse(team.can_apply(paltman))

    def test_can_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertFalse(team.can_apply(paltman))

    def test_can_join_non_member(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertTrue(team.can_join(paltman))

    def test_can_join_invited(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        membership = team.add_user(paltman, MembershipRole.MEMBER)
        membership.status = MembershipStatus.INVITED
        membership.save()
        self.assertTrue(team.can_join(User.objects.get(username="paltman")))

    def test_can_join_declined(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        membership = team.add_user(paltman, MembershipRole.MEMBER)
        membership.status = MembershipStatus.DECLINED
        membership.save()
        self.assertFalse(team.can_join(paltman))


class ManagerInviteMemberApplicationTests(BaseTeamTests):


    def test_cannot_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        team.add_user(paltman, MembershipRole.MEMBER)
        self.assertFalse(team.can_apply(paltman))

    def test_can_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertTrue(team.can_apply(paltman))

    def test_can_join_non_member(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertFalse(team.can_join(paltman))

    def test_can_join_invited(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        membership = team.add_user(paltman, MembershipRole.MEMBER)
        membership.status = MembershipStatus.INVITED
        membership.save()
        self.assertTrue(team.can_join(User.objects.get(username="paltman")))

    def test_can_join_declined(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        membership = team.add_user(paltman, MembershipRole.MEMBER)
        membership.status = MembershipStatus.DECLINED
        membership.save()
        self.assertFalse(team.can_join(paltman))


class ManagerInviteMemberInvitationTests(BaseTeamTests):

    def test_cannot_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        team.add_user(paltman, MembershipRole.MEMBER)
        self.assertFalse(team.can_apply(paltman))

    def test_can_apply(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertFalse(team.can_apply(paltman))

    def test_can_join_non_member(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        self.assertFalse(team.can_join(paltman))

    def test_can_join_invited(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        membership = team.add_user(paltman, MembershipRole.MEMBER)
        membership.status = MembershipStatus.INVITED
        membership.save()
        self.assertTrue(team.can_join(User.objects.get(username="paltman")))

    def test_can_join_declined(self):
        team = self._create_team()
        paltman = User.objects.create_user(username="paltman")
        membership = team.add_user(paltman, MembershipRole.MEMBER)
        membership.status = MembershipStatus.DECLINED
        membership.save()
        self.assertFalse(team.can_join(paltman))
