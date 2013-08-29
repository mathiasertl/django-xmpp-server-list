# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserConfirmationKey'
        db.create_table(u'confirm_userconfirmationkey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='confirmations', to=orm['auth.User'])),
        ))
        db.send_create_signal(u'confirm', ['UserConfirmationKey'])

        # Adding model 'UserPasswordResetKey'
        db.create_table(u'confirm_userpasswordresetkey', (
            (u'userconfirmationkey_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['confirm.UserConfirmationKey'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'confirm', ['UserPasswordResetKey'])

        # Adding model 'ServerConfirmationKey'
        db.create_table(u'confirm_serverconfirmationkey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(related_name='confirmations', to=orm['server.Server'])),
        ))
        db.send_create_signal(u'confirm', ['ServerConfirmationKey'])


    def backwards(self, orm):
        # Deleting model 'UserConfirmationKey'
        db.delete_table(u'confirm_userconfirmationkey')

        # Deleting model 'UserPasswordResetKey'
        db.delete_table(u'confirm_userpasswordresetkey')

        # Deleting model 'ServerConfirmationKey'
        db.delete_table(u'confirm_serverconfirmationkey')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'confirm.serverconfirmationkey': {
            'Meta': {'object_name': 'ServerConfirmationKey'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'confirmations'", 'to': u"orm['server.Server']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'confirm.userconfirmationkey': {
            'Meta': {'object_name': 'UserConfirmationKey'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'confirmations'", 'to': u"orm['auth.User']"})
        },
        u'confirm.userpasswordresetkey': {
            'Meta': {'object_name': 'UserPasswordResetKey', '_ormbases': [u'confirm.UserConfirmationKey']},
            u'userconfirmationkey_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['confirm.UserConfirmationKey']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'server.certificateauthority': {
            'Meta': {'object_name': 'CertificateAuthority'},
            'certificate': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'path': "'static/certs'", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'website': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'server.features': {
            'Meta': {'object_name': 'Features'},
            'has_ibr': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_ipv6': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_irc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_muc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_pep': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_plain': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_proxy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_ssl': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_tls': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_vcard': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_webpresence': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'server.server': {
            'Meta': {'object_name': 'Server'},
            'added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ca': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'servers'", 'to': u"orm['server.CertificateAuthority']"}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'contact_type': ('django.db.models.fields.CharField', [], {'default': "'J'", 'max_length': '1'}),
            'contact_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'}),
            'features': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'server'", 'unique': 'True', 'to': u"orm['server.Features']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'launched': ('django.db.models.fields.DateField', [], {}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'default': '<Point object at 0x2f1fe20>'}),
            'moderated': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'software': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'servers'", 'null': 'True', 'to': u"orm['server.ServerSoftware']"}),
            'software_version': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'ssl_port': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5223', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'servers'", 'to': u"orm['auth.User']"}),
            'verified': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'server.serversoftware': {
            'Meta': {'object_name': 'ServerSoftware'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'newest_version': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['confirm']
