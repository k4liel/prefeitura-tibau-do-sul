from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ReceitaResumo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ano", models.IntegerField(db_index=True)),
                (
                    "previsao",
                    models.DecimalField(decimal_places=2, default=0, max_digits=16),
                ),
                (
                    "arrecadacao",
                    models.DecimalField(decimal_places=2, default=0, max_digits=16),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DespesaSecretaria",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ano", models.IntegerField(db_index=True)),
                ("secretaria", models.CharField(max_length=255)),
                (
                    "orcamento",
                    models.DecimalField(decimal_places=2, default=0, max_digits=16),
                ),
                (
                    "empenhado",
                    models.DecimalField(decimal_places=2, default=0, max_digits=16),
                ),
                (
                    "liquidado",
                    models.DecimalField(decimal_places=2, default=0, max_digits=16),
                ),
                (
                    "pago",
                    models.DecimalField(decimal_places=2, default=0, max_digits=16),
                ),
            ],
        ),
    ]
