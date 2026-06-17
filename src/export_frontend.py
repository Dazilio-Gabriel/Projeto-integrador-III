import argparse
import json
from pathlib import Path

import pandas as pd

from src.config import DATA_PROCESSED, PROJECT_ROOT


FRONTEND_DIR = PROJECT_ROOT / "frontend"
DATA_PATH = FRONTEND_DIR / "data.js"


def export_frontend_data(input_path: str | Path = DATA_PROCESSED / "acidentes_bi.csv") -> Path:
    df = pd.read_csv(input_path)
    FRONTEND_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "summary": _summary(df),
        "records": _records(df),
        "options": {
            "municipios": _sorted_values(df, "municipio"),
            "rodovias": _sorted_values(df, "rodovia_label"),
            "riscos": _sorted_values(df, "nivel_risco"),
        },
    }

    DATA_PATH.write_text(
        "window.DASHBOARD_DATA = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    return DATA_PATH


def _summary(df: pd.DataFrame) -> dict:
    return {
        "total": int(len(df)),
        "alto_risco": int(df["risco_alto"].sum()) if "risco_alto" in df.columns else 0,
        "mortos": int(df["mortos"].sum()) if "mortos" in df.columns else 0,
        "feridos": int(df["feridos"].sum()) if "feridos" in df.columns else 0,
        "municipios": int(df["municipio"].nunique()) if "municipio" in df.columns else 0,
        "rodovias": int(df["rodovia_label"].nunique()) if "rodovia_label" in df.columns else 0,
    }


def _records(df: pd.DataFrame) -> list[dict]:
    columns = [
        "data_hora",
        "mes",
        "dia_semana",
        "hora_dia",
        "periodo_dia",
        "municipio",
        "regiao_grande_vitoria",
        "rodovia_label",
        "km",
        "latitude",
        "longitude",
        "causa",
        "tipo_acidente",
        "classificacao",
        "fase_dia",
        "condicao_metereologica",
        "tipo_pista",
        "mortos",
        "feridos_graves",
        "feridos_leves",
        "feridos",
        "veiculos",
        "pessoas",
        "risco_alto",
        "nivel_risco",
    ]
    available = [column for column in columns if column in df.columns]
    clean = df[available].copy()
    clean = clean.where(pd.notna(clean), None)
    return clean.to_dict(orient="records")


def _sorted_values(df: pd.DataFrame, column: str) -> list:
    if column not in df.columns:
        return []
    return sorted(value for value in df[column].dropna().unique().tolist())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exporta dados tratados para o dashboard frontend.")
    parser.add_argument(
        "--input",
        default=str(DATA_PROCESSED / "acidentes_bi.csv"),
        help="CSV tratado usado para alimentar o frontend.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    output = export_frontend_data(args.input)
    print(f"Dados do frontend exportados em: {output}")