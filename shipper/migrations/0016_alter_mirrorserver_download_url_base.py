# Generated by Django 3.2.3 on 2021-05-26 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipper', '0015_alter_mirrorserver_download_url_base'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mirrorserver',
            name='download_url_base',
            field=models.TextField(blank=True, help_text='Base of downloads URL, should a download URL exist.<br>Example: if full URL to download is https://sourceforge.net/projects/demo/files/Q/sunfish/Bliss-v14.2-sunfish-OFFICIAL-gapps-20210425.zip/download, then the base URL is https://sourceforge.net/projects/demo/files/Q/{}/download', max_length=100, verbose_name='Download URL base'),
        ),
    ]
