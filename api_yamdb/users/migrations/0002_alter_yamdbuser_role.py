# Generated by Django 3.2 on 2024-04-19 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yamdbuser',
            name='role',
            field=models.CharField(choices=[('USER', 'User'), ('MODERATOR', 'Moderator'), ('ADMIN', 'Admin')], default='USER', max_length=50, verbose_name='Роль'),
        ),
    ]
