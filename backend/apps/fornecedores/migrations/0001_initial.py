from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Fornecedor",
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
                ("nome", models.CharField(max_length=255)),
                ("cnpj", models.CharField(blank=True, max_length=30)),
                (
                    "valor_total",
                    models.DecimalField(decimal_places=2, default=0, max_digits=16),
                ),
            ],
            options={"ordering": ["-valor_total"]},
        )
    ]
