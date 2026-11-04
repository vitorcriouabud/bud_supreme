# Bud Supreme — recuperação controlada

Esta branch não executa trading real e não aplica automaticamente código gerado por IA.
Recupera inicialização, testes e backups; não é estratégia lucrativa validada.

## Instalação

Requer Python 3.11. Na raiz do repositório:

    python -m pip install -r requirements.txt
    python -m pytest -q tests
    python -m core.main

Com Docker, o comando padrão inicia o mesmo módulo core.main.

## Comandos

- status: consulta informações conhecidas, sem afirmar que MT5 está ativo.
- criar backup manual: grava um ZIP real e verifica integridade.
- executar testes: executa pytest, com retorno real e logs.
- Comandos de estratégia e risco: geram código em proposals/ para revisão.
  O arquivo de estratégia original não é modificado.

Os backups ficam em backups/ e excluem .env, bancos .db e virtualenvs.
Backups e propostas ficam ignorados pelo Git.
A análise estática do Guardian não é uma sandbox e não garante segurança.

## Limites

Sem trading real, ordens ao mercado, Pix, saques ou alterações automáticas em
produção. Esta branch não acrescenta integração com MetaTrader 5.
Para usar Telegram, configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID fora do Git.
Revise o pull request e valide os testes antes de mesclar.
