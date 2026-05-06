import io
import warnings

import pdfplumber
import pymysql
import pandas as pd
import numpy as np
import requests

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")


def _extrair_texto_pdf(url: str) -> str:
    """Baixa o PDF da URL e retorna seu conteúdo como texto."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        paginas = [pagina.extract_text() or "" for pagina in pdf.pages]
    return "\n\n".join(paginas)


def extrair_dados_acao(conn, sigla: str) -> dict:
    sigla = sigla.lower()
    sigla_up = sigla.upper()

    df_empresa = pd.read_sql(
        """
        SELECT sg.*, e.*
        FROM stock_guide sg
        LEFT JOIN empresa e ON sg.empresa_id = e.id
        WHERE LOWER(e.sigla) = %(sigla)s
        """,
        conn,
        params={"sigla": sigla},
    )
    if df_empresa.empty:
        raise ValueError(f"Nenhuma empresa encontrada para a sigla '{sigla}'")
    empresa_id = int(df_empresa["empresa_id"].iloc[0])

    # Recalcula margem_seguranca com cotacao_fechamento para não variar intraday
    if {"cotacao_fechamento", "preco_teto"}.issubset(df_empresa.columns):
        cf = df_empresa["cotacao_fechamento"]
        pt = df_empresa["preco_teto"]
        df_empresa["margem_seguranca"] = ((pt - cf) / cf * 100).round(4)
    df_empresa = df_empresa.drop(
        columns=["cotacao", "cotacao_variation", "cotacao_variation_percent"],
        errors="ignore",
    )

    queries = {
        "historico_resultado": "SELECT * FROM historico_resultado_empresa WHERE empresa_id = %(eid)s",
        "stock_guide_hist":    "SELECT * FROM stock_guide_historico      WHERE empresa_id = %(eid)s",
        "estimativa_tri":      "SELECT * FROM estimativa_tri             WHERE empresa_id = %(eid)s",
        "estimativa_hist":     "SELECT * FROM estimativa_historica       WHERE empresa_id = %(eid)s",
        "latest_analysis": """
            SELECT *
            FROM latest_analysis
            WHERE ticker = %(sigla_up)s
            ORDER BY date_analise DESC
            LIMIT 1
        """,
        "noticias": """
            SELECT n.data, n.titulo, n.conteudo
            FROM noticias n
            JOIN noticias_empresa ne ON ne.noticia_id = n.id
            WHERE ne.empresa_id = %(eid)s
              AND n.data >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
            ORDER BY n.data DESC
            LIMIT 20
        """,
        "recomendacao": """
            SELECT ticker, percent, comment, operation_type, updated_at
            FROM recomendacao
            WHERE ticker = %(sigla_up)s
            ORDER BY updated_at DESC
            LIMIT 1
        """,
    }

    params = {"eid": empresa_id, "sigla_up": sigla_up}
    dados = {"empresa": df_empresa}
    for nome, sql in queries.items():
        dados[nome] = pd.read_sql(sql, conn, params=params)

    # Extrai o conteúdo do PDF referenciado na coluna attachment (JSON array)
    df_analysis = dados["latest_analysis"]
    if not df_analysis.empty:
        attachment_raw = df_analysis["attachment"].iloc[0]
        if pd.notna(attachment_raw):
            import json
            itens = json.loads(attachment_raw) if isinstance(attachment_raw, str) else attachment_raw
            if itens and isinstance(itens, list):
                pdf_url = itens[0].get("url", "")
                if pdf_url:
                    texto_pdf = _extrair_texto_pdf(pdf_url)
                    dados["latest_analysis"] = df_analysis.assign(conteudo_pdf=[texto_pdf])

    return dados

conn = pymysql.connect(
    host="prd.db.agfmais.com.br", 
    port=3306,
    user="api-wealth-prd",
    password="207u{M5Ym)38;Kt",
    db="agfmais",
    connect_timeout=10)

# df = extrair_dados_acao(conn, "TASA4")
                   
#df_empresa   = dados["empresa"]
#df_resultado = dados["historico_resultado"]
#df_noticias  = dados["noticias"]
#analise_txt  = dados["latest_analysis"]["content"]
#noticias_txt = dados["noticias"]["conteudo"]


#(Média do DY em 5 anos): Mostra se a empresa paga bons dividendos de forma consistente ao longo do tempo.
#(DY Mínimo em 5 anos): Excelente para ver o "pior cenário". Mostra qual foi o menor rendimento entregue pela empresa recentemente.
#(CAGR de Dividendos): Mostra a taxa de crescimento anual composta dos dividendos. Empresas que aumentam seus lucros tendem a aumentar os dividendos, protegendo seu poder de compra contra a inflação.
#A taxa de crescimento dos lucros nos últimos anos. Fundamental para dividendos sustentáveis.


# Histórico de Lucro Líquido: A consistência é a principal métrica para o longo prazo. Companhias que mantêm um histórico de lucros crescentes ou estáveis são as melhores candidatas para uma carteira de renda.

# ROE (Return on Equity): Mede a capacidade da empresa de gerar valor com o dinheiro dos acionistas. Um ROE consistentemente alto, especialmente em setores robustos como o bancário ou de telecomunicações (como é o caso de papéis como BBAS3 e VIVT3), indica uma operação altamente eficiente e rentável.

# Margem Líquida: Mostra qual a porcentagem da receita que efetivamente se transforma em lucro. Ajuda a comparar o poder de precificação e a eficiência de custos de empresas dentro de um mesmo setor.

# Dívida Líquida / EBITDA: Avalia o nível de endividamento da empresa em relação à sua geração de caixa operacional. Empresas com dívidas elevadas e juros altos correm o risco de precisar cortar dividendos para honrar compromissos financeiros.

# Geração de Caixa Livre (Free Cash Flow): Os dividendos saem do caixa, e não apenas do lucro contábil. Uma empresa precisa gerar caixa operacional suficiente para cobrir suas necessidades de investimento em capital (CAPEX) e ainda ter capital excedente para distribuir aos sócios.

# relatórios gaudi

# sql = f"""
# SELECT *
# FROM latest_analysis
# """
# df = pd.read_sql(sql, conn)
# df['content']
# # noticias
# sql = f"""
# SELECT *
# FROM noticias
# """
# df = pd.read_sql(sql, conn)
# df['conteudo']

# with conn.cursor() as cursor:
#     cursor.execute("SHOW TABLES;")
#     print(cursor.fetchall())

# sql = f"""
# SELECT *
# FROM recomendacao
# """
# df = pd.read_sql(sql, conn)
