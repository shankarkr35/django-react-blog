# Generated by Django 4.2 on 2024-06-16 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('image', models.FileField(blank=True, null=True, upload_to='image')),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
        ),
    ]
