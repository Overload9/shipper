# Generated by Django 3.2.3 on 2021-05-26 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipper', '0011_alter_mirrorserver_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mirrorserver',
            name='ssh_host_key',
        ),
        migrations.RemoveField(
            model_name='mirrorserver',
            name='ssh_host_key_type',
        ),
        migrations.AddField(
            model_name='mirrorserver',
            name='ssh_host_fingerprint',
            field=models.TextField(default='', help_text='SSH host fingerprint.', max_length=1000, verbose_name='SSH host fingerprint'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mirrorserver',
            name='ssh_host_fingerprint_type',
            field=models.TextField(default='', help_text='SSH host fingerprint type.<br>Example: ssh-rsa, etc.', max_length=20, verbose_name='SSH host fingerprint type'),
            preserve_default=False,
        ),
    ]
