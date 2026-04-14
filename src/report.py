import sys
import os
from datetime import date

from src.db import get_conn
from src.extractor import extrair_dados_acao


def montar_contexto(sigla: str) -> str:
    with get_conn() as conn:
        dados = extrair_dados_acao(conn, sigla)

    partes = [f"# Dados brutos — {sigla.upper()}\n"]
    for nome, df in dados.items():
        partes.append(f"\n## {nome} ({len(df)} linhas)\n")
        if df.empty:
            partes.append("_(sem dados)_\n")
        else:
            # limita linhas para caber no contexto do LLM
            amostra = df.head(50).to_markdown(index=False)
            partes.append(amostra + "\n")
    return "\n".join(partes)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m src.report SIGLA")
        sys.exit(1)

    sigla = sys.argv[1]
    os.makedirs("reports", exist_ok=True)
    out = f"reports/{sigla.upper()}_{date.today()}_dados.md"

    with open(out, "w", encoding="utf-8") as f:
        f.write(montar_contexto(sigla))

    print(f" Dados salvos em {out}")