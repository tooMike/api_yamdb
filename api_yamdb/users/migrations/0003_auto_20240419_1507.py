# Generated by Django 3.2 on 2024-04-19 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_yamdbuser_role'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='yamdbuser',
            options={'ordering': ('username',), 'verbose_name': 'пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AlterField(
            model_name='yamdbuser',
            name='role',
            field=models.CharField(choices=[('user', 'User'), ('moderator', 'Moderator'), ('admin', 'Admin')], default='user', max_length=50, verbose_name='Роль'),
        ),
    ]
