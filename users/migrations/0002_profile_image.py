# Generated by Django 5.1.6 on 2025-02-18 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='aus.jpg', upload_to='user-profile'),
            preserve_default=False,
        ),
    ]
