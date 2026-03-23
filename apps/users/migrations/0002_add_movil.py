from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarjetasistema',
            name='movil',
            field=models.CharField(default='', max_length=15),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='solicitudacreditacion',
            name='sms_confirmacion',
            field=models.CharField(max_length=100),
        ),
    ]
