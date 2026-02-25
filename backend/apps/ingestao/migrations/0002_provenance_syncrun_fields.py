from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ingestao", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="syncrun",
            name="erro_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="syncrun",
            name="registro_count",
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name="DataProvenance",
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
                ("endpoint", models.CharField(max_length=255)),
                ("recurso", models.CharField(max_length=120)),
                ("external_id", models.CharField(blank=True, max_length=120)),
                ("payload_hash", models.CharField(db_index=True, max_length=64)),
                ("versao", models.CharField(default="v1", max_length=30)),
                ("coletado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-coletado_em"]},
        ),
        migrations.AddIndex(
            model_name="dataprovenance",
            index=models.Index(
                fields=["fonte", "recurso"], name="ingestao_dat_fonte_0c7e7f_idx"
            ),
        ),
    ]
