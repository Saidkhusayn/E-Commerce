# Generated by Django 5.0.6 on 2024-07-18 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_category_listing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='categoryName',
            field=models.CharField(choices=[('none', ''), ('electronics', 'Electronics'), ('fashion', 'Fashion'), ('toys', 'Toys'), ('home', 'Home'), ('other', 'Other')], max_length=50),
        ),
    ]
