# Generated by Django 3.0.8 on 2020-07-21 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_suggestion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='genres',
            field=models.CharField(default='', max_length=512),
        ),
        migrations.AddField(
            model_name='movie',
            name='keywords',
            field=models.CharField(default='', max_length=512),
        ),
        migrations.AddField(
            model_name='person',
            name='imdb_id',
            field=models.CharField(default='', max_length=20),
        ),
    ]
