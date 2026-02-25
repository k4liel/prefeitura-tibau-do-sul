from django.db import migrations, models


def dedupe_hashes(apps, schema_editor):
    DataProvenance = apps.get_model("ingestao", "DataProvenance")
    seen = set()
    to_delete = []
    for item in DataProvenance.objects.order_by("id").only("id", "payload_hash"):
        if item.payload_hash in seen:
            to_delete.append(item.id)
        else:
            seen.add(item.payload_hash)
    if to_delete:
        DataProvenance.objects.filter(id__in=to_delete).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("ingestao", "0002_provenance_syncrun_fields"),
    ]

    operations = [
        migrations.RunPython(dedupe_hashes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="dataprovenance",
            name="payload_hash",
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
