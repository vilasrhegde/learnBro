# Generated by Django 4.2.3 on 2023-07-06 06:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_room_options_room_participants'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['-updated', '-created']},
        ),
    ]
