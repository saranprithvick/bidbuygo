from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('bidbuygo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.CharField(max_length=50, unique=True, null=True, blank=True),
        ),
    ] 