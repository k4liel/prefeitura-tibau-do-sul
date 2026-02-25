from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("legislativo", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="vereador",
            constraint=models.UniqueConstraint(
                fields=("nome", "mandato"), name="uniq_vereador_nome_mandato"
            ),
        )
    ]
