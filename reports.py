"""Reusable report generation and CSV formatting."""
import csv
import io


def to_csv(rows: list[dict], columns: list[tuple[str, str]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([label for _, label in columns])
    for row in rows:
        writer.writerow([row.get(key, "") for key, _ in columns])
    return output.getvalue()
