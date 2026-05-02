"""SQL dosyalarını sırayla çalıştırır: schema -> views -> triggers -> procedures."""
from pathlib import Path
from sqlalchemy import text
from app.db.session import engine

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
ORDER = ["01_schema.sql", "02_views.sql", "03_triggers.sql", "04_procedures.sql"]


def run() -> None:
    with engine.begin() as conn:
        for name in ORDER:
            path = SQL_DIR / name
            print(f"-> Running {name} ...")
            sql = path.read_text(encoding="utf-8")
            conn.execute(text(sql))
    print("OK: Veritabanı şeması, view'lar, trigger'lar ve procedure'lar yüklendi.")


if __name__ == "__main__":
    run()
