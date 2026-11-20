"""Package the synthetic agenda data in an editable Power BI project."""

import base64
import json
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMAS = "https://developer.microsoft.com/json-schemas/fabric"
REPORT = HERE / "Agenda.Report"
MODEL = HERE / "Agenda.SemanticModel"
PAGE = "9cd3aee01ba449cdb803"
TABLE = "Agenda"
MEASURES = {
    "Agendamentos": ("COUNTROWS(Agenda)", "#,0"),
    "Cancelamentos": ('CALCULATE([Agendamentos], Agenda[desfecho] = "cancelado")', "#,0"),
    "Faltas": ('CALCULATE([Agendamentos], Agenda[desfecho] = "falta")', "#,0"),
    "Elegíveis": (
        'CALCULATE([Agendamentos], Agenda[desfecho] IN {"realizado", "falta"})', "#,0"
    ),
    "Taxa de falta": ("DIVIDE([Faltas], [Elegíveis])", "0.00%"),
}


def save(path, data, schema=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if schema:
        data = {"$schema": f"{SCHEMAS}/{schema}/schema.json", **data}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")


def build_model():
    source = (HERE.parent / "resultados" / "agendamentos.csv").read_bytes()
    compressor = zlib.compressobj(level=9, wbits=-15)
    encoded = base64.b64encode(compressor.compress(source) + compressor.flush()).decode("ascii")
    query = [
        "let",
        f'    Bytes = Binary.Decompress(Binary.FromText("{encoded}", BinaryEncoding.Base64), Compression.Deflate),',
        '    Csv = Csv.Document(Bytes, [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
        "    Headers = Table.PromoteHeaders(Csv, [PromoteAllScalars=true]),",
        '    Fields = Table.SelectColumns(Headers, {"id", "data_prevista", "unidade_id", "turno", "desfecho"}),',
        '    Unit = Table.AddColumn(Fields, "unidade", each Record.Field([N="Norte", S="Sul", C="Centro"], [unidade_id]), type text),',
        '    Month = Table.AddColumn(Unit, "mes", each Text.Start([data_prevista], 7), type text),',
        '    Output = Table.TransformColumnTypes(Table.RemoveColumns(Month, {"unidade_id"}), {{"id", Int64.Type}})',
        "in",
        "    Output",
    ]
    columns = [
        {"name": name, "sourceColumn": name, "dataType": data_type, "summarizeBy": "none"}
        for name, data_type in (
            ("id", "int64"), ("data_prevista", "string"), ("unidade", "string"),
            ("turno", "string"), ("desfecho", "string"), ("mes", "string"),
        )
    ]
    table = {
        "name": TABLE,
        "columns": columns,
        "measures": [
            {"name": name, "expression": expression, "formatString": fmt}
            for name, (expression, fmt) in MEASURES.items()
        ],
        "partitions": [{"name": TABLE, "mode": "import", "source": {"type": "m", "expression": query}}],
    }
    save(MODEL / "definition.pbism", {"version": "4.2", "settings": {"qnaEnabled": False}},
         "item/semanticModel/definitionProperties/1.0.0")
    save(MODEL / "model.bim", {
        "name": "Agenda Analytics", "compatibilityLevel": 1600,
        "model": {"culture": "pt-BR", "defaultPowerBIDataSourceVersion": "powerBI_V3", "tables": [table]},
    })


def projection(field_type, name):
    return {
        "field": {field_type: {"Expression": {"SourceRef": {"Entity": TABLE}}, "Property": name}},
        "queryRef": f"{TABLE}.{name}",
        "active": True,
    }


def add_visual(page, number, kind, position, roles, title):
    name = f"{number:020x}"
    x, y, width, height = position
    data = {
        "name": name,
        "position": {"x": x, "y": y, "z": number * 1000, "width": width,
                     "height": height, "tabOrder": number * 1000},
        "visual": {"visualType": kind, "query": {"queryState": {
            role: {"projections": [projection(field_type, field)]}
            for role, (field_type, field) in roles.items()
        }}, "visualContainerObjects": {"title": [{"properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
        }}]}},
    }
    save(page / "visuals" / name / "visual.json", data, "item/report/definition/visualContainer/2.0.0")


def build_report():
    save(HERE / "Agenda.pbip", {"version": "1.0", "artifacts": [{"report": {"path": REPORT.name}}]},
         "pbip/pbipProperties/1.0.0")
    save(REPORT / "definition.pbir", {
        "version": "4.0", "datasetReference": {"byPath": {"path": f"../{MODEL.name}"}},
    }, "item/report/definitionProperties/2.0.0")
    definition = REPORT / "definition"
    base_theme = {
        "name": "CY25SU12", "type": "SharedResources",
        "reportVersionAtImport": {"visual": "2.5.0", "report": "3.1.0", "page": "2.3.0"},
    }
    save(definition / "report.json", {"themeCollection": {"baseTheme": base_theme}},
         "item/report/definition/report/3.1.0")
    save(definition / "version.json", {"version": "2.0.0"}, "item/report/definition/versionMetadata/1.0.0")
    pages = definition / "pages"
    save(pages / "pages.json", {"pageOrder": [PAGE], "activePageName": PAGE},
         "item/report/definition/pagesMetadata/1.0.0")
    page = pages / PAGE
    save(page / "page.json", {
        "name": PAGE, "displayName": "Agenda Analytics | Dados sintéticos",
        "displayOption": "FitToPage", "width": 1280, "height": 720,
    }, "item/report/definition/page/2.0.0")
    for number, label in enumerate(("Agendamentos", "Cancelamentos", "Faltas", "Taxa de falta"), 1):
        add_visual(page, number, "card", (32 + (number - 1) * 308, 28, 288, 140),
                   {"Fields": ("Measure", label)}, label)
    add_visual(page, 5, "barChart", (32, 184, 600, 492), {
        "Category": ("Column", "unidade"), "Series": ("Column", "turno"), "Y": ("Measure", "Faltas"),
    }, "Faltas por unidade e turno")
    add_visual(page, 6, "lineChart", (648, 184, 600, 492), {
        "Category": ("Column", "mes"), "Y": ("Measure", "Taxa de falta"),
    }, "Taxa de falta por mês")


if __name__ == "__main__":
    build_model()
    build_report()
