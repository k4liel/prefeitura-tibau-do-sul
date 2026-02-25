from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("financas", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="receitaresumo",
            constraint=models.UniqueConstraint(
                fields=("ano",), name="uniq_receita_ano"
            ),
        ),
        migrations.AddIndex(
            model_name="despesasecretaria",
            index=models.Index(
                fields=["ano", "secretaria"], name="financas_de_ano_89df8a_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="despesasecretaria",
            constraint=models.UniqueConstraint(
                fields=("ano", "secretaria"), name="uniq_despesa_ano_secretaria"
            ),
        ),
    ]
