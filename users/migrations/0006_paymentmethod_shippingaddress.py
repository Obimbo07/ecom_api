# Generated by Django 5.1.6 on 2025-02-25 02:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_blacklistedtoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method_type', models.CharField(default='mpesa', max_length=50)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('last_four', models.CharField(blank=True, max_length=4, null=True)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=200, null=True)),
                ('address_line1', models.CharField(max_length=200)),
                ('address_line2', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('postal_code', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=100)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_addresses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
