from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pessoal", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="servidor",
            name="matricula",
            field=models.CharField(blank=True, db_index=True, max_length=80),
        ),
        migrations.AddIndex(
            model_name="servidor",
            index=models.Index(
                fields=["orgao", "vinculo"], name="pessoal_ser_orgao_2f1642_idx"
            ),
        ),
    ]
