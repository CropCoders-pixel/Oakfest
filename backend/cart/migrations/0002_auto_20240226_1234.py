from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='added_at',
            new_name='created_at',
        ),
    ]
