from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Licitacao",
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
                ("certame", models.CharField(blank=True, max_length=100)),
                ("modalidade", models.CharField(blank=True, max_length=120)),
                ("objeto", models.TextField(blank=True)),
                (
                    "valor",
                    models.DecimalField(decimal_places=2, default=0, max_digits=16),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Contrato",
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
                ("numero", models.CharField(blank=True, max_length=100)),
                ("empresa", models.CharField(max_length=255)),
                ("modalidade", models.CharField(blank=True, max_length=120)),
                ("objeto", models.TextField(blank=True)),
                (
                    "valor",
                    models.DecimalField(decimal_places=2, default=0, max_digits=16),
                ),
            ],
        ),
    ]
