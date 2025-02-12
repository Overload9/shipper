from .exceptions import *
from .tasks import *


def handle_build(device, zip_file, md5_file):
    # Confirm file names of build and checksum files match
    checksum_file_name, checksum_file_ext = os.path.splitext(md5_file.name)
    if zip_file.name != checksum_file_name:
        raise UploadException('file_name_mismatch')

    build_file_name, build_file_ext = os.path.splitext(zip_file.name)
    try:
        _, version, codename, build_type, variant, date = build_file_name.split('-')
    except ValueError:
        raise UploadException('invalid_file_name')

    file_name_validity_check(device, build_file_name, build_type, codename, variant)

    # See if a file exists from a previous failed attempt
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, device.codename, zip_file.name)):
        os.remove(os.path.join(settings.MEDIA_ROOT, device.codename, zip_file.name))
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, device.codename, md5_file.name)):
        os.remove(os.path.join(settings.MEDIA_ROOT, device.codename, md5_file.name))

    build = Build(
        device=device,
        file_name=build_file_name,
        size=zip_file.size,
        version=version,
        variant=variant,
        zip_file=zip_file,
        md5_file=md5_file,
    )
    build.save()

    # Execute background tasks
    build_background_processing(build.id)


def handle_chunked_build(device, chunked_file, md5_value):
    build_file_name, build_file_ext = os.path.splitext(chunked_file.filename)
    try:
        _, version, codename, build_type, variant, date = build_file_name.split('-')
    except ValueError:
        raise UploadException('invalid_file_name')

    file_name_validity_check(device, build_file_name, build_type, codename, variant)

    target_file_full_path = os.path.join(settings.MEDIA_ROOT, device.codename, chunked_file.filename)

    # See if the build exists from a previous failed attempt
    if os.path.exists(target_file_full_path):
        os.remove(target_file_full_path)

    # Make sure device codename folder exists
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, device.codename)):
        os.mkdir(os.path.join(settings.MEDIA_ROOT, device.codename))

    # Rename chunked file and move to correct folder
    os.rename(chunked_file.file.path, target_file_full_path)

    # Generate MD5 file
    md5_file_contents = "{}  {}".format(md5_value, chunked_file.filename)
    with open(os.path.join(settings.MEDIA_ROOT, device.codename, "{}.md5".format(chunked_file.filename)), 'w') \
            as target_md5:
        target_md5.write(md5_file_contents)

    build = Build(
        device=device,
        file_name=build_file_name,
        size=os.path.getsize(target_file_full_path),
        version=version,
        variant=variant,
        zip_file="{}/{}".format(device.codename, chunked_file.filename),
        md5_file="{}/{}.md5".format(device.codename, chunked_file.filename),
    )
    build.save()

    # Delete unused chunked_upload file
    chunked_file.delete()

    # Execute background tasks
    build_background_processing(build.id)


def build_background_processing(build_id):
    generate_sha256.delay(build_id)
    backup_build.delay(build_id)


def file_name_validity_check(device, build_file_name, build_type, codename, variant):
    if build_type != "OFFICIAL":
        raise UploadException('not_official')

    if codename != device.codename:
        raise UploadException('codename_mismatch')

    if Build.objects.filter(file_name=build_file_name).count() >= 1:
        raise UploadException('duplicate_build')

    if variant not in ["gapps", "vanilla", "foss", "goapps"]:
        raise UploadException('invalid_file_name')
