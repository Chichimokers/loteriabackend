from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loteria', '0002_update_tirada'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tirada',
            name='es_recurrente',
        ),
        migrations.RemoveField(
            model_name='tirada',
            name='pick_3',
        ),
        migrations.RemoveField(
            model_name='tirada',
            name='pick_4',
        ),
        migrations.CreateModel(
            name='Resultado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('pick_3', models.CharField(blank=True, max_length=3, null=True)),
                ('pick_4', models.CharField(blank=True, max_length=4, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tirada', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resultados', to='loteria.tirada')),
            ],
            options={
                'verbose_name': 'Resultado',
                'verbose_name_plural': 'Resultados',
                'ordering': ['-fecha', '-tirada__hora'],
                'unique_together': {('tirada', 'fecha')},
            },
        ),
    ]
