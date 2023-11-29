# Generated by Django 4.2.6 on 2023-11-21 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_discountproduct_discount_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('M', 'Men'), ('W', 'Woman'), ('K', 'Kids')], max_length=1, null=True),
        ),
    ]