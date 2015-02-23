# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Role', fields ['name', 'team']
        db.delete_unique(u'teamwork_role', ['name', 'team_id'])

        # Adding model 'Member'
        db.create_table(u'teamwork_member', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamwork.Team'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamwork.Role'], null=True)),
            ('is_owner', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, db_index=True, blank=True)),
        ))
        db.send_create_signal(u'teamwork', ['Member'])

        # Deleting field 'Team.founder'
        db.delete_column(u'teamwork_team', 'founder_id')

        # Deleting field 'Role.team'
        db.delete_column(u'teamwork_role', 'team_id')

        # Adding field 'Role.created'
        db.add_column(u'teamwork_role', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2015, 2, 22, 0, 0), db_index=True, blank=True),
                      keep_default=False)

        # Adding field 'Role.modified'
        db.add_column(u'teamwork_role', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, db_index=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field users on 'Role'
        db.delete_table(db.shorten_name(u'teamwork_role_users'))

        # Adding M2M table for field permissions_denied on 'Role'
        m2m_table_name = db.shorten_name(u'teamwork_role_permissions_denied')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('role', models.ForeignKey(orm[u'teamwork.role'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['role_id', 'permission_id'])

        # Adding unique constraint on 'Role', fields ['name']
        db.create_unique(u'teamwork_role', ['name'])

        # Deleting field 'Policy.anonymous'
        db.delete_column(u'teamwork_policy', 'anonymous')

        # Deleting field 'Policy.apply_to_owners'
        db.delete_column(u'teamwork_policy', 'apply_to_owners')

        # Adding field 'Policy.all'
        db.add_column(u'teamwork_policy', 'all',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Policy.owners'
        db.add_column(u'teamwork_policy', 'owners',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding M2M table for field permissions_denied on 'Policy'
        m2m_table_name = db.shorten_name(u'teamwork_policy_permissions_denied')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('policy', models.ForeignKey(orm[u'teamwork.policy'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['policy_id', 'permission_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Role', fields ['name']
        db.delete_unique(u'teamwork_role', ['name'])

        # Deleting model 'Member'
        db.delete_table(u'teamwork_member')

        # Adding field 'Team.founder'
        db.add_column(u'teamwork_team', 'founder',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Role.team'
        db.add_column(u'teamwork_role', 'team',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=999, to=orm['teamwork.Team']),
                      keep_default=False)

        # Deleting field 'Role.created'
        db.delete_column(u'teamwork_role', 'created')

        # Deleting field 'Role.modified'
        db.delete_column(u'teamwork_role', 'modified')

        # Adding M2M table for field users on 'Role'
        m2m_table_name = db.shorten_name(u'teamwork_role_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('role', models.ForeignKey(orm['teamwork.role'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['role_id', 'user_id'])

        # Removing M2M table for field permissions_denied on 'Role'
        db.delete_table(db.shorten_name(u'teamwork_role_permissions_denied'))

        # Adding unique constraint on 'Role', fields ['name', 'team']
        db.create_unique(u'teamwork_role', ['name', 'team_id'])

        # Adding field 'Policy.anonymous'
        db.add_column(u'teamwork_policy', 'anonymous',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Policy.apply_to_owners'
        db.add_column(u'teamwork_policy', 'apply_to_owners',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'Policy.all'
        db.delete_column(u'teamwork_policy', 'all')

        # Deleting field 'Policy.owners'
        db.delete_column(u'teamwork_policy', 'owners')

        # Removing M2M table for field permissions_denied on 'Policy'
        db.delete_table(db.shorten_name(u'teamwork_policy_permissions_denied'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'teamwork.member': {
            'Meta': {'object_name': 'Member'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamwork.Role']", 'null': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamwork.Team']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'teamwork.policy': {
            'Meta': {'object_name': 'Policy'},
            'all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'authenticated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'creator'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'owners': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'policies_granted'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'permissions_denied': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'policies_denied'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamwork.Team']", 'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'teamwork.role': {
            'Meta': {'object_name': 'Role'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'roles_granted'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'permissions_denied': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'roles_denied'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'teamwork.team': {
            'Meta': {'object_name': 'Team'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'through': u"orm['teamwork.Member']", 'symmetrical': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'})
        }
    }

    complete_apps = ['teamwork']