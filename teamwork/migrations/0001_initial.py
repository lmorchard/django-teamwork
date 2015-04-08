# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(null=True, verbose_name='Description of policy')),
                ('object_id', models.PositiveIntegerField()),
                ('anonymous', models.BooleanField(default=False, help_text='Apply this policy to anonymous users?')),
                ('authenticated', models.BooleanField(default=False, help_text='Apply this policy to authenticated users?')),
                ('apply_to_owners', models.BooleanField(default=False, help_text='Apply this policy to owners of content objects?')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(db_index=True, auto_now=True, null=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('creator', models.ForeignKey(related_name='creator', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('groups', models.ManyToManyField(help_text='Apply this policy for these user groups.', to='auth.Group', blank=True)),
                ('permissions', models.ManyToManyField(help_text='Permissions granted by this policy', related_name='permissions', verbose_name='permissions', to='auth.Permission', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Policies',
                'permissions': (('view_policy', 'Can view policy'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('description', models.TextField(verbose_name='Description of intended use', blank=True)),
                ('permissions', models.ManyToManyField(help_text='Specific permissions for this role.', to='auth.Permission', blank=True)),
            ],
            options={
                'permissions': (('view_role', 'Can view role'), ('manage_role_permissions', 'Can manage role permissions'), ('manage_role_users', 'Can manage role users')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128, verbose_name='name', db_index=True)),
                ('description', models.TextField(null=True, verbose_name='Description of intended use', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(db_index=True, auto_now=True, null=True)),
                ('founder', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('view_team', 'Can view team'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='role',
            name='team',
            field=models.ForeignKey(to='teamwork.Team'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='role',
            name='users',
            field=models.ManyToManyField(help_text='Users granted this role', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('name', 'team')]),
        ),
        migrations.AddField(
            model_name='policy',
            name='team',
            field=models.ForeignKey(blank=True, to='teamwork.Team', help_text='Team responsible for managing this policy', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='policy',
            name='users',
            field=models.ManyToManyField(help_text='Apply this policy for these users.', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
    ]
