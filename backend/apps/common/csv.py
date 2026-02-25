import csv

from django.http import HttpResponse


class CSVListExportMixin:
    csv_filename = "export.csv"

    def list(self, request, *args, **kwargs):
        if request.query_params.get("export") == "csv":
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return self._to_csv_response(serializer.data)
        return super().list(request, *args, **kwargs)

    def _to_csv_response(self, rows):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{self.csv_filename}"'
        writer = csv.writer(response, delimiter=";")
        if rows:
            headers = list(rows[0].keys())
            writer.writerow(headers)
            for row in rows:
                writer.writerow([row.get(h, "") for h in headers])
        return response
