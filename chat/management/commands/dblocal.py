from django.core.management.base import BaseCommand
from django.utils import autoreload
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = "Adjust and Create DB local"

    def handle(self, *args, **options):
        os.environ["DJANGO_SETTINGS_MODULE"] = "settings.dev"

        #necessary to reload in manage.py with new value of DJANGO_SETTINGS_MODULE
        autoreload.main(self.inner_run, args, options)
        self.stdout.write('Successfully execute Command dblocal.\n')

    def inner_run(self, *args, **options):
        self.stdout.write("called dblocal using %s .\n" % os.environ["DJANGO_SETTINGS_MODULE"])
        autoreload.exit_code = 3
        call_command('syncdb')
        call_command('migrate', 'chat')
        try:
            call_command('schemamigration', 'chat', auto=True)
            #if schemamigration execute eith sucess execute migrate gain
            call_command('migrate', 'chat')
        except:
            #schemamigration return error if not have new changes with option auto=true :(
            pass

        #stop this new thread seting this RUN_RELOADER
        autoreload.RUN_RELOADER = False
