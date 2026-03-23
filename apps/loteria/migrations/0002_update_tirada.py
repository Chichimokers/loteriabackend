from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loteria', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tirada',
            name='es_recurrente',
            field=models.BooleanField(default=False, help_text='Si es True, se repite todos los días a la hora indicada'),
        ),
        migrations.AlterField(
            model_name='tirada',
            name='fecha',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RemoveConstraint(
            model_name='tirada',
            name='loteria_tirada_hora_fecha_unique',
        ),
        migrations.AddConstraint(
            model_name='tirada',
            constraint=models.UniqueConstraint(fields=('loteria', 'hora', 'fecha'), name='unique_tirada_fecha'),
        ),
        migrations.AddConstraint(
            model_name='tirada',
            constraint=models.UniqueConstraint(fields=('loteria', 'hora'), condition=models.Q(fecha__isnull=True), name='unique_tirada_recurrente'),
        ),
    ]
