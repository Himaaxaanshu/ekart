# Generated by Django 5.0.2 on 2024-03-06 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomapp', '0002_cart_orders'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='static/images'),
        ),
    ]
