# Generated by Django 3.2.15 on 2023-01-15 18:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0004_actel_keyid'),
    ]

    operations = [
        migrations.AddField(
            model_name='actel',
            name='name_ar',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='doleance',
            name='dateReview',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='doleance',
            name='satisfy',
            field=models.SmallIntegerField(choices=[(0, 'Positive'), (1, 'Neutre'), (2, 'Négative')], default=1, validators=[django.core.validators.MaxValueValidator(2), django.core.validators.MinValueValidator(0)], verbose_name='Satisfaction'),
        ),
    ]
