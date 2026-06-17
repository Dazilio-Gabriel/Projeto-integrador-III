from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

RANDOM_STATE = 42
TEST_SIZE = 0.25

GRANDE_VITORIA = {
    "vitoria",
    "vila velha",
    "serra",
    "cariacica",
    "viana",
    "guarapari",
    "fundao",
}