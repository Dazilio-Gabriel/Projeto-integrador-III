import re
import unicodedata

import numpy as np
import pandas as pd

from src.config import GRANDE_VITORIA


ALIASES = {
    "data": ["data", "data_inversa", "data_acidente", "dt_acidente"],
    "hora": ["hora", "horario", "hora_acidente", "hr_acidente"],
    "municipio": ["municipio", "cidade", "município"],
    "uf": ["uf", "estado"],
    "rodovia": ["br", "rodovia", "via"],
    "km": ["km", "quilometro"],
    "bairro": ["bairro"],
    "latitude": ["latitude", "lat"],
    "longitude": ["longitude", "lng", "lon", "long"],
    "causa": ["causa_acidente", "causa", "causa_principal"],
    "tipo_acidente": ["tipo_acidente", "tipo", "natureza_acidente"],
    "classificacao": ["classificacao_acidente", "classificacao", "gravidade"],
    "fase_dia": ["fase_dia", "fase_do_dia"],
    "sentido_via": ["sentido_via", "sentido"],
    "condicao_metereologica": ["condicao_metereologica", "condicao_meteorologica", "clima"],
    "tipo_pista": ["tipo_pista", "pista"],
    "tracado_via": ["tracado_via", "tracado"],
    "uso_solo": ["uso_solo"],
    "mortos": ["mortos", "obitos", "vitimas_fatais"],
    "feridos_graves": ["feridos_graves", "feridos_grave"],
    "feridos_leves": ["feridos_leves"],
    "feridos": ["feridos"],
    "ilesos": ["ilesos"],
    "ignorados": ["ignorados"],
    "veiculos": ["veiculos", "qtd_veiculos", "quantidade_veiculos"],
    "pessoas": ["pessoas", "qtd_pessoas", "quantidade_pessoas"],
    "regional": ["regional"],
    "delegacia": ["delegacia"],
    "uop": ["uop"],
}


def filter_scope(df: pd.DataFrame, uf: str | None = "ES", grande_vitoria_only: bool = False) -> pd.DataFrame:
    result = df.copy()
    if uf and "uf" in result.columns:
        result = result[result["uf"].astype(str).str.upper().eq(uf.upper())].copy()

    if grande_vitoria_only and "regiao_grande_vitoria" in result.columns:
        result = result[result["regiao_grande_vitoria"]].copy()

    return result


def clean_column_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(name))
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_name = re.sub(r"[^0-9a-zA-Z]+", "_", ascii_name.strip().lower())
    return re.sub(r"_+", "_", ascii_name).strip("_")


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.copy()
    renamed.columns = [clean_column_name(column) for column in renamed.columns]
    renamed = renamed.loc[:, ~renamed.columns.str.startswith("unnamed")]
    renamed = renamed.dropna(axis=1, how="all")

    reverse_aliases = {}
    for canonical, aliases in ALIASES.items():
        for alias in aliases:
            reverse_aliases[clean_column_name(alias)] = canonical

    column_map = {}
    used_names = set()
    for column in renamed.columns:
        canonical = reverse_aliases.get(column)
        if canonical and canonical not in used_names:
            column_map[column] = canonical
            used_names.add(canonical)

    return renamed.rename(columns=column_map)


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    result = standardize_columns(df)
    result = _strip_text_columns(result)
    result = _parse_datetime(result)
    result = _parse_numeric_fields(result)
    result = _add_spatial_flags(result)
    result = _add_risk_target(result)
    result = _add_road_labels(result)
    return result


def build_bi_dataset(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    useful_columns = [
        "data",
        "hora",
        "data_hora",
        "ano",
        "mes",
        "dia_semana",
        "hora_dia",
        "periodo_dia",
        "uf",
        "municipio",
        "regiao_grande_vitoria",
        "rodovia",
        "rodovia_label",
        "km",
        "bairro",
        "latitude",
        "longitude",
        "causa",
        "tipo_acidente",
        "classificacao",
        "fase_dia",
        "sentido_via",
        "condicao_metereologica",
        "tipo_pista",
        "tracado_via",
        "uso_solo",
        "mortos",
        "feridos_graves",
        "feridos_leves",
        "feridos",
        "ilesos",
        "ignorados",
        "veiculos",
        "pessoas",
        "regional",
        "delegacia",
        "uop",
        "risco_alto",
        "nivel_risco",
    ]
    return result[[column for column in useful_columns if column in result.columns]]


def _add_road_labels(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if "rodovia" in result.columns:
        road = pd.to_numeric(result["rodovia"], errors="coerce")
        result["rodovia_label"] = road.map(lambda value: f"BR-{int(value)}" if pd.notna(value) else np.nan)
    return result


def _strip_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in result.select_dtypes(include=["object"]).columns:
        result[column] = result[column].astype(str).str.strip()
        result[column] = result[column].replace({"": np.nan, "nan": np.nan, "None": np.nan})
    return result


def _parse_datetime(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if "data" in result.columns:
        result["data"] = _parse_date_series(result["data"])

    if "hora" in result.columns:
        result["hora"] = result["hora"].astype(str).str.extract(r"(\d{1,2}:\d{2})", expand=False)

    if "data" in result.columns and "hora" in result.columns:
        result["data_hora"] = pd.to_datetime(
            result["data"].dt.strftime("%Y-%m-%d") + " " + result["hora"],
            errors="coerce",
        )
    elif "data" in result.columns:
        result["data_hora"] = result["data"]

    if "data_hora" in result.columns:
        result["ano"] = result["data_hora"].dt.year
        result["mes"] = result["data_hora"].dt.month
        result["dia_semana"] = result["data_hora"].dt.dayofweek.map(
            {
                0: "segunda",
                1: "terca",
                2: "quarta",
                3: "quinta",
                4: "sexta",
                5: "sabado",
                6: "domingo",
            }
        )
        result["hora_dia"] = result["data_hora"].dt.hour
        result["periodo_dia"] = pd.cut(
            result["hora_dia"],
            bins=[-1, 5, 11, 17, 23],
            labels=["madrugada", "manha", "tarde", "noite"],
        )

    return result


def _parse_date_series(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip()
    iso_mask = text.str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)

    parsed = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
    parsed.loc[iso_mask] = pd.to_datetime(text.loc[iso_mask], errors="coerce", format="%Y-%m-%d")
    parsed.loc[~iso_mask] = pd.to_datetime(text.loc[~iso_mask], errors="coerce", dayfirst=True)
    return parsed


def _parse_numeric_fields(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    numeric_columns = [
        "km",
        "latitude",
        "longitude",
        "mortos",
        "feridos_graves",
        "feridos_leves",
        "feridos",
        "ilesos",
        "ignorados",
        "veiculos",
        "pessoas",
    ]
    for column in numeric_columns:
        if column in result.columns:
            result[column] = (
                result[column]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .str.replace(r"[^0-9.\-]", "", regex=True)
            )
            result[column] = pd.to_numeric(result[column], errors="coerce")
    return result


def _add_spatial_flags(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if "municipio" in result.columns:
        normalized_municipio = result["municipio"].astype(str).map(clean_column_name)
        normalized_municipio = normalized_municipio.str.replace("_", " ")
        result["regiao_grande_vitoria"] = normalized_municipio.isin(GRANDE_VITORIA)
    return result


def _add_risk_target(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    fatal = _numeric_or_zero(result, "mortos") > 0
    severe = _numeric_or_zero(result, "feridos_graves") > 0

    text_signal = pd.Series(False, index=result.index)
    for column in ["classificacao", "tipo_acidente"]:
        if column in result.columns:
            lowered = result[column].astype(str).str.lower()
            text_signal = text_signal | lowered.str.contains("fatal|morto|obito|grave", regex=True, na=False)

    result["risco_alto"] = (fatal | severe | text_signal).astype(int)

    conditions = [
        fatal,
        severe | text_signal,
        _numeric_or_zero(result, "feridos_leves") > 0,
    ]
    choices = ["fatal", "grave", "moderado"]
    result["nivel_risco"] = np.select(conditions, choices, default="baixo")
    return result


def _numeric_or_zero(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(0, index=df.index)
    return pd.to_numeric(df[column], errors="coerce").fillna(0)