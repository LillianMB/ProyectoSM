# Generated by Django 5.1.6 on 2025-03-24 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_alter_calificaciones_archivotarea'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.CharField(blank=True, choices=[('Scrum Master', 'Scrum Master'), ('Developer', 'Developer'), ('Product Owner', 'Product Owner')], max_length=100, null=True),
        ),
    ]
