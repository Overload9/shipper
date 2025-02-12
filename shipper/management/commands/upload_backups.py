from django.core.management import BaseCommand

from shipper.models import Build, MirrorServer
from shipper.tasks import backup_build


class Command(BaseCommand):
    help = "Uploads builds that haven't been backed up yet."

    def handle(self, *args, **options):
        # Get all builds that are not mirrored on all enabled mirrors
        enabled_mirrors = list(MirrorServer.objects.filter(enabled=True))
        builds = Build.objects.exclude(mirrored_on__in=enabled_mirrors)

        for build in builds:
            self.stdout.write("Backing up build {}...".format(build.file_name))
            backup_build.delay(build.id)
            self.stdout.write("Queued backup for build {}!".format(build.file_name))

        self.stdout.write("Queued all incomplete builds. Please check the admin panel for status updates.")
