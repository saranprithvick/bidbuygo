from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('bidbuygo', '0011_add_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='full_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='phone_number',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='address_line1',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='address_line2',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='state',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='postal_code',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='country',
            field=models.CharField(max_length=50, default='India', null=True),
        ),
    ] 