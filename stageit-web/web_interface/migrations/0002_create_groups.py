from django.db import migrations, models
from django.conf import settings
from django.contrib.auth.models import Group, User, Permission
from django.apps import apps as django_apps


# https://stackoverflow.com/questions/50114505/why-i-cant-assign-new-permission-to-group-in-the-same-migration-in-django
def post_migrate_signal(apps, schema_editor):
    config = django_apps.get_app_config('web_interface')
    models.signals.post_migrate.send(
        sender=config,
        app_config=config,
        verbosity=2,
        interactive=False,
        using=schema_editor.connection.alias,
    )


def add_groups(apps, schema_editor):

    Group.objects.create(name="Workers")
    Group.objects.create(name="Users")


def assign_permissions(apps, schema_editor):
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
        migrations.RunPython(add_groups),
        migrations.RunPython(post_migrate_signal),
        migrations.RunPython(assign_permissions),
    ]
