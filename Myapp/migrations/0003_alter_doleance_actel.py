# Generated by Django 3.2.15 on 2023-01-10 11:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0002_doleance_actel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doleance',
            name='actel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Doleance', to='Myapp.actel'),
        ),
    ]
