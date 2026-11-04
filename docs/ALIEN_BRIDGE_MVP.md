# Bud–ALIEN — Contrato de observação offline (MVP)

Este protótipo **não é conexão ao MetaTrader 5**. Ele aceita arquivos JSON de
amostra e gera observações verificáveis sobre a qualidade dos dados.
O primeiro arquivo contém valores totalmente sintéticos, não preços reais.

## Executar

Requer Python 3.11, sem nenhuma chave de API:

    python -m alien_bridge examples/alien_xauusd_snapshot.json
    python -m pytest -q tests

Comando de saída com status 0: JSON de diagnóstico no console.
JSON inválido, caminho ausente ou registro inconsistente: erro no stderr e exit 2.

## Contrato de entrada `alien-market-v1`

Campos obrigatórios e únicos no nível superior:

- `schema_version`: exatamente `alien-market-v1`
- `source`: apenas `synthetic`, `historical` ou `demo`
- `symbol`: símbolo ASCII limitado a 25 caracteres seguros
- `timeframe`: `M1`, `M5`, `M15`, `H1`
- `captured_at`: ISO-8601 com fuso
- `spread`: distância de preço não negativa (não pontos)
- `bars`: 1–2000 candles ordenados, cada um com
  `time` (ISO-8601 com fuso), `open`, `high`, `low`,
  `close`, `volume`. OHLC positivo, volume não negativo.

Lê até 1 MB por arquivo. Duplicatas, valores não finitos, candles posteriores
à captura ou chaves extras (incluindo senhas/tokens) são rejeitados.

## Indicadores de qualidade de dados

- `gaps_detected`: lacunas de tempo maiores que o timeframe
- `stale`: último candle mais antigo que 2 intervalos
- `spread_to_average_range`: spread dividido pela amplitude média da amostra
- `high_relative_spread`: comparação heurística, não um sinal de trading

O resultado inclui explicitamente `trading_enabled=false` e `orders_sent=0`.
Nenhum módulo deste MVP faz chamadas de rede nem importa MetaTrader5.

## Próximo incremento

Testar em demo um **exportador separado** de snapshots anonimizados do MT5
e fornecer novos arquivos a este observador. O exportador deverá ser auditado
para garantir que NÃO envia ordens nem expõe login, saldo, senha ou token.
Somente depois de uma validação de ponta a ponta poderemos dizer que há
integração real. O ALIEN V10.89 não foi alterado.

O fluxo de autoedição do Bud Supreme continua protegido pelo PR #4.
Esta branch cria um PR separado para revisão.
