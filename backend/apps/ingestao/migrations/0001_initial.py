from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SyncRun",
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
                ("fonte", models.CharField(max_length=120)),
                ("status", models.CharField(default="pendente", max_length=30)),
                ("iniciado_em", models.DateTimeField(auto_now_add=True)),
                ("finalizado_em", models.DateTimeField(blank=True, null=True)),
                ("mensagem", models.TextField(blank=True)),
            ],
            options={"ordering": ["-iniciado_em"]},
        )
    ]
