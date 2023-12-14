# Generated by Django 4.2 on 2023-10-19 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casestudy', '0004_alter_email_body_alter_email_eid_alter_email_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='body',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='email',
            name='eid',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='email',
            name='status',
            field=models.CharField(blank=True, default='', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='email',
            name='subject',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='email',
            name='to_recipient',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
