#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sample_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
            
    if len(sys.argv) == 5 and sys.argv[1] == "createsuperuser":
        # when used as python manage.py createsuperuser <username> <email> <password>
        import django
        django.setup()
        from django.contrib.auth.models import User
        superuser = User.objects.create_superuser(sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) == 5 and sys.argv[1] == "getorcreatesuperuser":
        # when used as python manage.py getorcreatesuperuser <username> <email> <password>
        import django
        django.setup()
        from django.contrib.auth.models import User
        users = User.objects.filter(username=sys.argv[2])
        if len(users) == 0:
            superuser = User.objects.create_superuser(sys.argv[2], sys.argv[3], sys.argv[4])
            print( "New superuser created" )
        else:
            superuser = users[0]
            print( "Existing superuser found" )
    else:    
        execute_from_command_line(sys.argv)
