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
        if nome == "latest_analysis":
            _render_latest_analysis(df, partes)
            continue
        if nome == "noticias":
            _render_noticias(df, partes)
            continue
        if nome == "recomendacao":
            _render_recomendacao(df, partes)
            continue

        partes.append(f"\n## {nome} ({len(df)} linhas)\n")
        if df.empty:
            partes.append("_(sem dados)_\n")
        else:
            # limita linhas para caber no contexto do LLM
            amostra = df.head(50).to_markdown(index=False)
            partes.append(amostra + "\n")
    return "\n".join(partes)


def _render_noticias(df, partes: list) -> None:
    """Renderiza notícias como lista de itens título + conteúdo."""
    partes.append("\n## noticias (últimos 3 meses)\n")
    if df.empty:
        partes.append("_(sem notícias no período)_\n")
        return

    for _, row in df.iterrows():
        data_str = str(row.get("data", ""))[:10]
        titulo = str(row.get("titulo", "")).strip()
        conteudo = str(row.get("conteudo", "")).strip()
        partes.append(f"### {data_str} — {titulo}\n")
        if conteudo:
            partes.append(conteudo + "\n")


def _render_recomendacao(df, partes: list) -> None:
    """Renderiza recomendação da carteira AGF."""
    partes.append("\n## recomendacao\n")
    if df.empty:
        partes.append("- **Na carteira recomendada AGF:** Não\n")
        return
    row = df.iloc[0]
    partes.append(f"- **Na carteira recomendada AGF:** Sim")
    partes.append(f"- **Operação:** {row.get('operation_type', '')}")
    partes.append(f"- **Peso na carteira:** {row.get('percent', '')}%")
    partes.append(f"- **Atualizado em:** {str(row.get('updated_at', ''))[:10]}")
    comentario = str(row.get("comment", "")).strip()
    if comentario:
        partes.append(f"- **Comentário AGF:** {comentario}\n")


def _render_latest_analysis(df, partes: list) -> None:
    """Renderiza latest_analysis como metadados + texto corrido do PDF."""
    partes.append("\n## latest_analysis\n")
    if df.empty:
        partes.append("_(sem dados)_\n")
        return

    row = df.iloc[0]
    partes.append(f"- **ticker:** {row.get('ticker', '')}")
    partes.append(f"- **date_analise:** {row.get('date_analise', '')}")
    partes.append(f"- **autor:** {row.get('content', '')}\n")

    conteudo = row.get("conteudo_pdf", "")
    if conteudo:
        partes.append("### Conteúdo do relatório (PDF)\n")
        partes.append(str(conteudo) + "\n")
    else:
        partes.append("_(sem PDF extraído)_\n")


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