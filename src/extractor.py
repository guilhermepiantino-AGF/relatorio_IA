import pymysql
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

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

    queries = {
        "historico_resultado": "SELECT * FROM historico_resultado_empresa WHERE empresa_id = %(eid)s",
        "stock_guide_hist":    "SELECT * FROM stock_guide_historico      WHERE empresa_id = %(eid)s",
        "estimativa_tri":      "SELECT * FROM estimativa_tri             WHERE empresa_id = %(eid)s",
        "estimativa_hist":     "SELECT * FROM estimativa_historica       WHERE empresa_id = %(eid)s",
        #"latest_analysis":     "SELECT * FROM latest_analysis            WHERE ticker     = %(sigla_up)s",
    }

    params = {"eid": empresa_id, "sigla_up": sigla_up}
    dados = {"empresa": df_empresa}
    for nome, sql in queries.items():
        dados[nome] = pd.read_sql(sql, conn, params=params)

    return dados

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
# FROM noticias_empresa
# """
# df = pd.read_sql(sql, conn)
# df['conteudo']

