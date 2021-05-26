import hashlib
import os
import time
from contextlib import contextmanager

import paramiko
import pysftp
from celery import shared_task
from django.core.cache import cache
from django.db import transaction
from paramiko.py3compat import decodebytes

from config import settings
from shipper.models import Build, MirrorServer


@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = time.monotonic() + settings.CELERY_TASK_TIME_LIMIT - 3
    status = cache.add(lock_id, oid, settings.CELERY_TASK_TIME_LIMIT)
    try:
        yield status
    finally:
        if time.monotonic() < timeout_at and status:
            cache.delete(lock_id)


@shared_task
def process_incomplete_builds():
    builds = Build.objects.filter(sha256sum__exact='')

    for build in builds:
        generate_sha256.delay(build.id)

    builds = Build.objects.filter(backed_up=False)

    for build in builds:
        backup_build.delay(build.id)


# noinspection SpellCheckingInspection
@shared_task(bind=True)
def backup_build(self, build_id):
    build = Build.objects.get(id=build_id)
    mirrors = MirrorServer.objects.filter(enabled=True)

    # Check if there are any servers to back up to
    if len(mirrors) == 0:
        print("No mirror servers found to back up to. Exiting...")
        return

    # Check if a previous run has already completed a backup
    if build.backed_up:
        return

    # Setup lock
    lock_id = '{}-lock-{}'.format(self.name, build.id)
    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            for mirror in mirrors:
                # Check if a previous run has already completed a backup
                if mirror in build.mirrored_on:
                    continue

                keydata = mirror.ssh_host_key
                key = paramiko.RSAKey(data=decodebytes(keydata))
                cnopts = pysftp.CnOpts()
                cnopts.hostkeys.add(mirror.hostname, mirror.ssh_host_key_type, key)

                with pysftp.Connection(
                        host=mirror.hostname,
                        username=mirror.ssh_username,
                        private_key=mirror.ssh_keyfile,
                        cnopts=cnopts
                ) as sftp:
                    sftp.cwd(mirror.upload_path)

                    if not sftp.exists(build.device.codename):
                        sftp.mkdir(build.device.codename)

                    sftp.cwd(build.device.codename)

                    sftp.put(os.path.join(settings.MEDIA_ROOT, build.zip_file.name))
                    sftp.put(os.path.join(settings.MEDIA_ROOT, build.md5_file.name))

                # Fetch build one more time and lock until save completes
                with transaction.atomic():
                    build = Build.objects.select_for_update().get(id=build_id)
                    build.mirrored_on.add(mirror)
                    build.save()
        else:
            print("Build {} is already being backed up by another process, exiting!".format(build.file_name))


@shared_task
def generate_sha256(build_id):
    build = Build.objects.get(id=build_id)

    # Check if this task has already been run
    if build.sha256sum not in [None, '']:
        print("SHA256 generated by another process, exiting!")
        return

    sha256sum = hashlib.sha256()
    with open(os.path.join(settings.MEDIA_ROOT, build.zip_file.name), 'rb') as destination:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: destination.read(4096), b""):
            sha256sum.update(byte_block)

    # Fetch build one more time and lock until save completes
    with transaction.atomic():
        build = Build.objects.select_for_update().get(id=build_id)
        build.sha256sum = sha256sum.hexdigest()
        build.save()
