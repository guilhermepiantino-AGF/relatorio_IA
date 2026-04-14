Gere um relatório de análise para uma ação. Argumentos recebidos: $ARGUMENTS

Formato esperado dos argumentos: "SIGLA TIPO"
Exemplo: "BBAS3 investimento" ou "BBAS3 qualitativa"

Passos:
1. Extraia SIGLA (primeiro argumento) e TIPO (segundo argumento)
2. Se TIPO não for informado, use "investimento" como padrão
3. Execute no terminal: `python -m src.report <SIGLA>`
4. Leia o arquivo mais recente em reports/<SIGLA>_*_dados.md
5. Leia o template em prompts/analise_<TIPO>.md
   - Se o arquivo não existir, liste os templates disponíveis em prompts/
     e pergunte qual usar antes de continuar
6. Aplique RIGOROSAMENTE a estrutura e as regras do template aos dados
7. Salve o relatório final em reports/<SIGLA>_<YYYY-MM-DD>_<TIPO>.md
8. Ao final, mostre o caminho do arquivo gerado
