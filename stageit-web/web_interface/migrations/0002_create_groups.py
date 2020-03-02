from django.contrib.auth.models import Permission
from django.db import migrations
from django.conf import settings
from django.contrib.auth.models import Group, User


def add_workers_group(apps, schema_editor):

    Group.objects.create(name="Workers")
    # get_or_create returns a tuple, not a Group
    group = Group.objects.get(name="Workers")
    permissions = Permission.objects.filter(codename__in=[
        'add_log',
        'change_history',
        'delete_task',
        'view_bootstrapconfig',
        'view_firmware',
        'view_history',
        'view_log',
        'view_remoteworker',
        'view_serialport',
        'view_task',
        'view_template',
        'view_terminalserver',
    ])
    group.permissions.add(*permissions)


def add_users_group(apps, schema_editor):

    Group.objects.create(name="Users")
    # get_or_create returns a tuple, not a Group
    group = Group.objects.get(name="Users")
    permissions = Permission.objects.filter(codename__in=[
        'add_bootstrapconfig',
        'add_firmware',
        'add_history',
        'add_log',
        'add_remoteworker',
        'add_serialport',
        'add_task',
        'add_template',
        'add_terminalserver',
        'change_bootstrapconfig',
        'change_firmware',
        'change_history',
        'change_log',
        'change_remoteworker',
        'change_serialport',
        'change_task',
        'change_template',
        'change_terminalserver',
        'delete_bootstrapconfig',
        'delete_firmware',
        'delete_history',
        'delete_log',
        'delete_remoteworker',
        'delete_serialport',
        'delete_task',
        'delete_template',
        'delete_terminalserver',
        'view_bootstrapconfig',
        'view_firmware',
        'view_history',
        'view_log',
        'view_remoteworker',
        'view_serialport',
        'view_task',
        'view_template',
        'view_terminalserver',
    ])
    group.permissions.add(*permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('web_interface', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_workers_group),
        migrations.RunPython(add_users_group),
    ]
