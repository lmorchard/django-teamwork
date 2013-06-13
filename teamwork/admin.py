from django.contrib import admin
from django.core.urlresolvers import reverse

from .models import Team, Role


def related_roles_link(self):
    """HTML link to related roles for admin change list"""
    link = '%s?%s' % (
        reverse('admin:teamwork_role_changelist', args=[]),
        'team__exact=%s' % (self.id)
    )
    count = self.role_set.count()
    what = (count == 1) and 'role' or 'roles'
    return '<a href="%s">%s&nbsp;%s</a>' % (link, count, what)

related_roles_link.allow_tags = True
related_roles_link.short_description = "Roles"


def team_link(self):
    """HTML link to a Team"""
    url = reverse('admin:teamwork_team_change', args=[self.team.pk])
    return '<a href="%s">Team: %s</a>' % (url, self.team)

team_link.allow_tags = True
team_link.short_description = 'Team'


class RoleAdmin(admin.ModelAdmin):
    raw_id_fields = ('team',) #'users',)
    list_select_related = True
    list_display = ('name', team_link,)
    search_fields = ('name', 'team__name',)
    filter_horizontal = ('users', 'permissions',)


class RoleInline(admin.TabularInline):
    model = Role
    fields = ('name','permissions','users',)
    filter_horizontal = ('users', 'permissions',)
    raw_id_fields = ('users',)
    extra = 0


class TeamAdmin(admin.ModelAdmin):
    fields = (
        'name', 'description', 'founder',
        'anonymous_permissions', 'authenticated_permissions',
    )
    raw_id_fields = ('founder',)
    list_select_related = True
    list_display = ('name', related_roles_link,)
    filter_horizontal = (
        'anonymous_permissions', 'authenticated_permissions',
    )
    search_fields = ('name',)
    inlines = (RoleInline,)


admin.site.register(Team, TeamAdmin)
admin.site.register(Role, RoleAdmin)
