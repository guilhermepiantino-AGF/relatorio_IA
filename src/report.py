import sys, os, json
from datetime import date
from src.db import get_conn
from src.extractor import extrair_dados_acao

def montar_contexto(sigla: str) -> str:
    with get_conn() as conn:
        dados = extrair_dados_acao(conn, sigla)

    partes = []
    for nome, df in dados.items():
        # limita p/ caber no contexto; ajuste conforme necessário
        amostra = df.head(20).to_markdown(index=False)
        partes.append(f"## {nome}\n\n{amostra}\n")
    return "\n".join(partes)

if __name__ == "__main__":
    sigla = sys.argv[1]
    contexto = montar_contexto(sigla)
    out = f"reports/{sigla}_{date.today()}_dados.md"
    os.makedirs("reports", exist_ok=True)
    with open(out, "w") as f:
        f.write(contexto)
    print(f"Dados salvos em {out}")