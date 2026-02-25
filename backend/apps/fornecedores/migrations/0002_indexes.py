from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fornecedores", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="fornecedor",
            index=models.Index(fields=["nome"], name="fornecedore_nome_7698f3_idx"),
        ),
        migrations.AddIndex(
            model_name="fornecedor",
            index=models.Index(fields=["cnpj"], name="fornecedore_cnpj_3ad08c_idx"),
        ),
    ]
