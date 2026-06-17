from pathlib import Path

import pandas as pd


def read_dataset(path: str | Path) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return _read_csv(file_path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)

    raise ValueError("Formato nao suportado. Use CSV, XLSX ou XLS.")


def _read_csv(path: Path) -> pd.DataFrame:
    encodings = ["utf-8", "latin1", "cp1252"]
    separators = [None, ";", ","]
    last_error: Exception | None = None

    for encoding in encodings:
        for separator in separators:
            try:
                return pd.read_csv(path, sep=separator, encoding=encoding, engine="python")
            except Exception as exc:  # pandas exposes different parser/codec errors
                last_error = exc

    raise ValueError(f"Nao foi possivel ler o CSV: {last_error}")


def save_csv(df: pd.DataFrame, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")