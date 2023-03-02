# Generated by Django 3.2.15 on 2023-02-05 15:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0010_auto_20230205_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='regdor',
            name='userat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur'),
        ),
    ]
