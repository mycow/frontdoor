# Generated by Django 2.0.3 on 2018-05-08 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_room_num_users_if_no_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lease',
            name='rentscalefactor',
            field=models.FloatField(null=True),
        ),
    ]
