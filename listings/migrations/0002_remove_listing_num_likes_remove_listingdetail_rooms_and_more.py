# Generated by Django 5.1.6 on 2025-03-01 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='num_likes',
        ),
        migrations.RemoveField(
            model_name='listingdetail',
            name='rooms',
        ),
        migrations.AddField(
            model_name='listing',
            name='price',
            field=models.DecimalField(decimal_places=2, default='0', max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listing',
            name='rooms',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listingdetail',
            name='num_likes',
            field=models.IntegerField(default=0),
        ),
    ]
