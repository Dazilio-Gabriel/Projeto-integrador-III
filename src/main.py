import argparse

from src.config import DATA_PROCESSED, FIGURES_DIR, REPORTS_DIR
from src.data_io import read_dataset, save_csv
from src.eda import descriptive_summary, export_aggregation_tables, generate_figures
from src.export_frontend import export_frontend_data
from src.model import train_risk_model
from src.preprocessing import build_bi_dataset, filter_scope, preprocess


def run(input_path: str, uf: str | None = "ES", grande_vitoria_only: bool = False) -> None:
    raw = read_dataset(input_path)
    treated = filter_scope(preprocess(raw), uf=uf, grande_vitoria_only=grande_vitoria_only)
    grande_vitoria = treated[treated["regiao_grande_vitoria"]].copy() if "regiao_grande_vitoria" in treated.columns else treated.iloc[0:0]
    bi = build_bi_dataset(treated)
    bi_grande_vitoria = build_bi_dataset(grande_vitoria)

    save_csv(treated, DATA_PROCESSED / "acidentes_tratados.csv")
    bi_path = DATA_PROCESSED / "acidentes_bi.csv"
    save_csv(bi, bi_path)
    save_csv(grande_vitoria, DATA_PROCESSED / "acidentes_grande_vitoria.csv")
    save_csv(bi_grande_vitoria, DATA_PROCESSED / "acidentes_bi_grande_vitoria.csv")
    save_csv(descriptive_summary(treated), REPORTS_DIR / "resumo_descritivo.csv")
    save_csv(descriptive_summary(grande_vitoria), REPORTS_DIR / "resumo_descritivo_grande_vitoria.csv")
    tables = export_aggregation_tables(treated, REPORTS_DIR)
    figures = generate_figures(treated, FIGURES_DIR)
    frontend_data = export_frontend_data(bi_path)
    model_outputs = train_risk_model(treated, REPORTS_DIR)

    print("Pipeline concluido.")
    print(f"Registros analisados: {len(treated)}")
    print(f"Filtro UF: {uf or 'sem filtro'}")
    print(f"Somente Grande Vitoria: {'sim' if grande_vitoria_only else 'nao'}")
    print(f"Base tratada: {DATA_PROCESSED / 'acidentes_tratados.csv'}")
    print(f"Base para BI: {DATA_PROCESSED / 'acidentes_bi.csv'}")
    print(f"Base Grande Vitoria: {DATA_PROCESSED / 'acidentes_grande_vitoria.csv'}")
    print(f"Resumo: {REPORTS_DIR / 'resumo_descritivo.csv'}")
    print(f"Dados do frontend: {frontend_data}")
    print(f"Tabelas agregadas geradas: {len(tables)}")
    print(f"Graficos gerados: {len(figures)}")
    if model_outputs:
        print(f"Metricas do modelo: {model_outputs['metrics']}")
        print(f"Modelo treinado: {model_outputs['model']}")
    else:
        print("Modelo nao treinado: base pequena, alvo ausente ou apenas uma classe de risco.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline de analise de acidentes de transito.")
    parser.add_argument("--input", required=True, help="Caminho do arquivo CSV/XLSX original.")
    parser.add_argument("--uf", default="ES", help="UF analisada. Use vazio com --uf '' para nao filtrar.")
    parser.add_argument(
        "--grande-vitoria",
        action="store_true",
        help="Restringe a analise aos municipios da Grande Vitoria.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.input, uf=args.uf or None, grande_vitoria_only=args.grande_vitoria)