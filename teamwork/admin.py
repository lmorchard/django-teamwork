from django.contrib import admin
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User, Permission

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from .models import Team, Membership, Role, Policy


def related_memberships_link(self):
    """HTML link to related Memberships for admin change list"""
    link = '%s?%s' % (
        reverse('admin:teamwork_membership_changelist', args=[]),
        'team__exact=%s' % (self.id)
    )
    count = self.members.count()
    what = (count == 1) and 'Membership' or 'Memberships'
    return '<a href="%s">%s&nbsp;%s</a>' % (link, count, what)

related_memberships_link.allow_tags = True
related_memberships_link.short_description = "Memberships"


def team_link(self):
    """HTML link to a Team"""
    url = reverse('admin:teamwork_team_change', args=[self.team.pk])
    return '<a href="%s">Team: %s</a>' % (url, self.team)

team_link.allow_tags = True
team_link.short_description = 'Team'


class PolicyAdmin(admin.ModelAdmin):
    fields = (
        'content_type', 'object_id',
        'team', 'creator',
        'permissions',
        'apply_to_owners',
        'anonymous', 'authenticated',
        'users', 'groups',
    )
    raw_id_fields = ('users', 'creator',)
    related_lookup_fields = {
        'fk': ['creator'],
        'm2m': ['users'],
        'generic': [['content_type', 'object_id'], ]
    }
    list_select_related = True
    filter_horizontal = ('permissions', 'groups', 'users',)


class PolicyInline(generic.GenericTabularInline):
    """Policy inline editor for content objects that constrains Permission
    choices to the content type"""
    model = Policy
    fields = (
        'team', 'creator',
        'permissions',
        'apply_to_owners',
        'anonymous', 'authenticated',
        'users', 'groups',
    )
    filter_horizontal = ('permissions', 'groups', 'users',)
    raw_id_fields = ('users', 'creator',)
    extra = 0

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("authenticated_permissions",
                             "anonymous_permissions"):
            ct = ContentType.objects.get_for_model(self.parent_model)
            kwargs["queryset"] = (Permission.objects
                                            .filter(content_type__pk=ct.id))
        return super(PolicyInline, self).formfield_for_manytomany(
            db_field, request, **kwargs)


class RoleAdmin(admin.ModelAdmin):
    raw_id_fields = ('team',)
    list_select_related = True
    list_display = ('name', team_link,)
    search_fields = ('name', 'team__name',)
    filter_horizontal = ('permissions',)


class RoleInline(admin.TabularInline):
    model = Role
    fields = ('name', 'permissions',)
    filter_horizontal = ('permissions',)
    extra = 0


class TeamAdmin(admin.ModelAdmin):
    fields = ( 'name', 'description' )
    list_select_related = True
    list_display = ('name', related_memberships_link,)
    search_fields = ('name',)
    inlines = (RoleInline,)


class MembershipAdmin(admin.ModelAdmin):
    fields = ('team', 'user', 'role')
    raw_id_fields = ('user',)
    list_select_related = True
    list_display = ('team', 'user', 'role')



admin.site.register(Team, TeamAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Policy, PolicyAdmin)
