# Generated by Django 4.2 on 2023-10-19 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casestudy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='eid',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='email',
            name='status',
            field=models.CharField(default='', max_length=25),
        ),
        migrations.AlterField(
            model_name='email',
            name='subject',
            field=models.CharField(default='', max_length=255),
        ),
    ]
