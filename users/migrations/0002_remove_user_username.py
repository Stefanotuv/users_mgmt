# Generated by Django 4.2.3 on 2023-07-18 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="user", name="username",),
    ]
