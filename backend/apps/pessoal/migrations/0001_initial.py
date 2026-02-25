from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Servidor",
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
                ("orgao", models.CharField(max_length=255)),
                ("vinculo", models.CharField(blank=True, max_length=80)),
                (
                    "valor_bruto",
                    models.DecimalField(decimal_places=2, default=0, max_digits=14),
                ),
                (
                    "valor_liquido",
                    models.DecimalField(decimal_places=2, default=0, max_digits=14),
                ),
            ],
            options={"ordering": ["nome"]},
        )
    ]
