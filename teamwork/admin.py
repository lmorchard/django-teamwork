from django.contrib import admin
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User, Permission

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from .models import Team, Member, Role, Policy


def related_members_link(self):
    """HTML link to related Members for admin change list"""
    link = '%s?%s' % (
        reverse('admin:teamwork_member_changelist', args=[]),
        'team__exact=%s' % (self.id)
    )
    count = self.members.count()
    what = (count == 1) and 'Member' or 'Members'
    return '<a href="%s">%s&nbsp;%s</a>' % (link, count, what)

related_members_link.allow_tags = True
related_members_link.short_description = "Members"


def team_link(self):
    """HTML link to a Team"""
    url = reverse('admin:teamwork_team_change', args=[self.team.pk])
    return '<a href="%s">Team: %s</a>' % (url, self.team)

team_link.allow_tags = True
team_link.short_description = 'Team'


def role_link(self):
    """HTML link to a role"""
    if not self.role:
        return 'None'
    url = reverse('admin:teamwork_role_change', args=[self.role.pk])
    return '<a href="%s">Role: %s</a>' % (url, self.role)

role_link.allow_tags = True
role_link.short_description = 'role'


class PolicyAdmin(admin.ModelAdmin):
    fields = (
        'content_type', 'object_id',
        'team', 'creator',
        'permissions', 'permissions_denied',
        'all', 'authenticated',
        'owners',
        'users', 'groups',
    )
    raw_id_fields = ('users', 'creator',)
    related_lookup_fields = {
        'fk': ['creator'],
        'm2m': ['users'],
        'generic': [['content_type', 'object_id'], ]
    }
    list_select_related = True
    filter_horizontal = ('permissions', 'permissions_denied', 'groups', 'users',)


class PolicyInline(generic.GenericTabularInline):
    """Policy inline editor for content objects that constrains Permission
    choices to the content type"""
    model = Policy
    fields = (
        'team', 'creator',
        'permissions',
        'all', 'authenticated',
        'owners',
        'users', 'groups',
    )
    filter_horizontal = ('permissions', 'permissions_denied', 'groups', 'users',)
    raw_id_fields = ('users', 'creator',)
    extra = 0


class RoleAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ('name', 'created', 'modified',)
    search_fields = ('name',)
    filter_horizontal = ('permissions', 'permissions_denied')


class RoleInline(admin.TabularInline):
    model = Role
    fields = ('name', 'permissions', 'permissions_denied')
    filter_horizontal = ('permissions', 'permissions_denied')
    extra = 0


class TeamAdmin(admin.ModelAdmin):
    fields = ( 'name', 'description' )
    list_select_related = True
    list_display = ('name', related_members_link, 'created', 'modified',)
    search_fields = ('name',)


class MemberAdmin(admin.ModelAdmin):
    fields = ('team', 'user', 'role', 'is_owner')
    raw_id_fields = ('user',)
    list_select_related = True
    list_display = ('id', 'user', team_link, role_link, 'is_owner', 'created', 'modified')



admin.site.register(Team, TeamAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Policy, PolicyAdmin)
