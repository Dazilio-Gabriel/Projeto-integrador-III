from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def descriptive_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = [
        ("total_registros", len(df)),
        ("total_colunas", len(df.columns)),
        ("acidentes_alto_risco", int(df["risco_alto"].sum()) if "risco_alto" in df.columns else 0),
        ("percentual_alto_risco", float(df["risco_alto"].mean()) if "risco_alto" in df.columns else 0),
    ]

    if "municipio" in df.columns:
        rows.append(("municipios_unicos", int(df["municipio"].nunique(dropna=True))))
    if "rodovia" in df.columns:
        rows.append(("rodovias_unicas", int(df["rodovia"].nunique(dropna=True))))
    if "data_hora" in df.columns:
        rows.append(("data_minima", df["data_hora"].min()))
        rows.append(("data_maxima", df["data_hora"].max()))

    return pd.DataFrame(rows, columns=["metrica", "valor"])


def export_aggregation_tables(df: pd.DataFrame, output_dir: str | Path) -> list[Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    specs = {
        "acidentes_por_municipio.csv": ["municipio"],
        "acidentes_por_rodovia.csv": ["rodovia_label"],
        "acidentes_por_rodovia_km.csv": ["rodovia_label", "km"],
        "acidentes_por_causa.csv": ["causa"],
        "acidentes_por_tipo.csv": ["tipo_acidente"],
        "acidentes_por_classificacao.csv": ["classificacao"],
        "acidentes_por_dia_semana.csv": ["dia_semana"],
        "acidentes_por_hora.csv": ["hora_dia"],
        "acidentes_por_mes.csv": ["mes"],
    }

    outputs = []
    for filename, group_columns in specs.items():
        if all(column in df.columns for column in group_columns):
            table = aggregate_by(df, group_columns)
            path = output_path / filename
            table.to_csv(path, index=False, encoding="utf-8-sig")
            outputs.append(path)

    return outputs


def aggregate_by(df: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    grouped = df.groupby(group_columns, dropna=False).size().reset_index(name="total_acidentes")

    sum_columns = ["risco_alto", "mortos", "feridos_graves", "feridos_leves", "feridos", "veiculos", "pessoas"]
    for column in sum_columns:
        if column in df.columns:
            values = df.groupby(group_columns, dropna=False)[column].sum().reset_index(name=column)
            grouped = grouped.merge(values, on=group_columns, how="left")

    if "risco_alto" in grouped.columns:
        grouped = grouped.rename(columns={"risco_alto": "acidentes_alto_risco"})
        grouped["percentual_alto_risco"] = grouped["acidentes_alto_risco"] / grouped["total_acidentes"]

    return grouped.sort_values("total_acidentes", ascending=False)


def generate_figures(df: pd.DataFrame, output_dir: str | Path) -> list[Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    figures = []
    specs = [
        ("hora_dia", "Acidentes por hora do dia", "acidentes_por_hora.png"),
        ("dia_semana", "Acidentes por dia da semana", "acidentes_por_dia_semana.png"),
        ("mes", "Acidentes por mes", "acidentes_por_mes.png"),
        ("municipio", "Top municipios por acidentes", "top_municipios.png"),
        ("causa", "Top causas de acidentes", "top_causas.png"),
        ("rodovia_label", "Top rodovias por acidentes", "top_rodovias.png"),
    ]

    for column, title, filename in specs:
        if column in df.columns:
            path = output_path / filename
            _plot_count(df, column, title, path)
            figures.append(path)

    return figures


def _plot_count(df: pd.DataFrame, column: str, title: str, path: Path) -> None:
    values = df[column].dropna()
    if values.empty:
        return

    order = values.value_counts().head(15).index
    plt.figure(figsize=(11, 6))
    sns.countplot(data=df[df[column].isin(order)], y=column, order=order, color="#2f80ed")
    plt.title(title)
    plt.xlabel("Quantidade")
    plt.ylabel(column)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()