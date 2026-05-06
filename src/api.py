"""
API FastAPI para geração de relatórios de análise de ações.

Uso:
    uvicorn src.api:app --reload

Endpoint:
    POST /analisar/{sigla}?tipo=investimento
"""

import json
import re
from datetime import date
from pathlib import Path

import anthropic
from fastapi import FastAPI, HTTPException, Query

from src.report import montar_contexto

app = FastAPI(title="Relatório AGF", version="1.0")

PROMPTS_DIR = Path("prompts")
REPORTS_DIR = Path("reports")
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 6000

# Preços por milhão de tokens (USD)
PRECO_INPUT_POR_M = 3.00
PRECO_OUTPUT_POR_M = 15.00

SECAO_SLUGS = {
    "1": "sumario",
    "2": "analise_dados_financeiros",
    "3": "apresentacao_empresa",
    "4": "analise_setorial",
    "5": "noticias_percepcao_recente",
}


def _carregar_template(tipo: str) -> str:
    path = PROMPTS_DIR / f"analise_{tipo}.md"
    if not path.exists():
        disponiveis = [p.stem.removeprefix("analise_") for p in PROMPTS_DIR.glob("analise_*.md")]
        raise HTTPException(
            status_code=404,
            detail=f"Template '{tipo}' não encontrado. Disponíveis: {disponiveis}",
        )
    return path.read_text(encoding="utf-8")


def _carregar_dados(sigla: str) -> str:
    try:
        return montar_contexto(sigla)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


def _parsear_secoes(sigla: str, tipo: str, relatorio: str) -> dict:
    partes = re.split(r"\n(?=## \d+\.)", relatorio)
    secoes = {}

    for parte in partes:
        m = re.match(r"## (\d+)\.\s+(.+)", parte)
        if m:
            chave = SECAO_SLUGS.get(m.group(1), f"secao_{m.group(1)}")
            secoes[chave] = parte.strip()
        elif parte.strip():
            secoes["cabecalho"] = parte.strip()

    return {
        "sigla": sigla,
        "data": str(date.today()),
        "tipo": tipo,
        "secoes": secoes,
    }


def _salvar(sigla: str, tipo: str, dados: str, relatorio: str, uso: dict) -> dict:
    REPORTS_DIR.mkdir(exist_ok=True)
    hoje = date.today()

    (REPORTS_DIR / f"{sigla}_{hoje}_dados.md").write_text(dados, encoding="utf-8")
    (REPORTS_DIR / f"{sigla}_{hoje}_{tipo}.md").write_text(relatorio, encoding="utf-8")

    resultado = _parsear_secoes(sigla, tipo, relatorio)
    resultado["uso"] = uso
    (REPORTS_DIR / f"{sigla}_{hoje}_{tipo}.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return resultado


@app.post("/analisar/{sigla}")
def analisar(
    sigla: str,
    tipo: str = Query(default="investimento", description="Tipo de relatório"),
) -> dict:
    sigla = sigla.upper()
    template = _carregar_template(tipo)
    dados = _carregar_dados(sigla)
    prompt = template.replace("{SIGLA}", sigla)

    client = anthropic.Anthropic()
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=prompt,
        messages=[{"role": "user", "content": dados}],
    ) as stream:
        msg = stream.get_final_message()

    relatorio = "".join(b.text for b in msg.content if b.type == "text")

    tokens_input = msg.usage.input_tokens
    tokens_output = msg.usage.output_tokens
    custo_usd = round(
        tokens_input * PRECO_INPUT_POR_M / 1_000_000
        + tokens_output * PRECO_OUTPUT_POR_M / 1_000_000,
        6,
    )

    uso = {
        "modelo": MODEL,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "custo_usd": custo_usd,
    }
    return _salvar(sigla, tipo, dados, relatorio, uso)


