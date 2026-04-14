import os
from contextlib import contextmanager

import pymysql
from dotenv import load_dotenv

load_dotenv()


def _config() -> dict:
    """Lê as credenciais do .env e devolve no formato do pymysql.connect()."""
    faltando = [
        k for k in ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
        if not os.getenv(k)
    ]
    if faltando:
        raise RuntimeError(
            f"Variáveis de ambiente ausentes: {', '.join(faltando)}. "
            "Verifique seu arquivo .env."
        )

    return {
        "host":            os.getenv("DB_HOST"),
        "port":            int(os.getenv("DB_PORT", "3306")),
        "user":            os.getenv("DB_USER"),
        "password":        os.getenv("DB_PASSWORD"),
        "db":              os.getenv("DB_NAME"),
        "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10")),
        "charset":         "utf8mb4",
    }


@contextmanager
def get_conn():
    """
    Context manager para uso com pandas:

        with get_conn() as conn:
            df = pd.read_sql("SELECT ...", conn)
    """
    conn = pymysql.connect(**_config())
    try:
        yield conn
    finally:
        conn.close()