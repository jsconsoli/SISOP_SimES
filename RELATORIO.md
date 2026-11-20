# Relatório — SimES: simulador de E/S e de sistema de arquivos

**Integrantes:** [nome completo de TODOS os integrantes, separados por vírgula]

**Repositório:** [https://github.com/usuario/repositorio — o repositório público do grupo]

<!--
INSTRUÇÕES DO MODELO (apaguem este bloco antes de entregar)
- Este relatório é a entrega: exportem-no para PDF e CADA integrante envia o PDF no Moodle.
- Nomes completos de todos os integrantes e o link do repositório público são obrigatórios
  (linhas acima). Não coloquem matrícula, e-mail, telefone ou outro dado pessoal.
- Mantenham EXATAMENTE os títulos numerados (## 0. ... ## 8.) e os campos em negrito.
- Na seção 3, mantenham X1 a X5 e só as seções dos experimentos do escopo do grupo
  (M1 = X6, M2 = X7, M3 = X8, M4 = X9, M5 = X10, M6 = X11, integração = X12, bônus = X13).
  Apaguem as seções dos experimentos que o grupo não fez.
- Substituam todo texto entre colchetes [ ... ] pelo conteúdo do grupo.
- O campo **Veredito:** aceita só: CONFIRMADA, PARCIALMENTE CONFIRMADA ou REFUTADA.
- Em **Evidências:**, citem arquivos que existam no repositório (resultados/..., graficos/...).
- Antes de entregar, rodem:  python3 ferramentas/validar_entrega.py
-->

## 0. Resumo

[Até 10 linhas: o que o grupo implementou, quais módulos escolheu e os 3 resultados mais importantes.]

## 1. Escopo realizado

| Parte | Situação | Observação |
|---|---|---|
| N1 · Dispositivo (fornecido) | usado | — |
| N2 · Subsistema de E/S (SSTF, SCAN, polling, interrupção) | [completo / parcial] | [ ] |
| N3 · Sistema de arquivos | [completo / parcial] | [ ] |
| N4 · Experimentos X1–X5 e relatório | [completo / parcial] | [ ] |
| M6 · Alocação em disco (encadeada, FAT, indexada) | completo | testes do M6 passam; X11 roda sem erros |
| Integração (grupos de 4) | completo | `historico_para_requisicoes` em `simes/integracao.py`; X12 roda sem erros |
| [Bônus flash] | [completo / parcial / não feito] | [ ] |

Resultado dos testes automáticos (`python3 executar.py testes`): [cole a última linha, ex.: "Ran 26 tests ... OK (skipped=6)"]

## 2. Implementação

### N2 — Subsistema de E/S

**Onde:** [arquivos e funções]

**Decisões:** [como implementaram SSTF, SCAN, polling e interrupção; casos especiais]

**Dificuldades:** [o que deu trabalho e como resolveram]

### N3 — Sistema de arquivos

**Onde:** [arquivos e funções]

**Decisões:** [resolução de caminhos, tabelas de arquivos abertos, leitura e escrita, unlink com arquivo aberto]

**Dificuldades:** [ ]

### M6 — Alocação em disco

**Onde:** `simes/arquivos/alocacao.py` (AlocadorEncadeado, AlocadorFAT, AlocadorIndexado).

**Decisões:** A encadeada guarda um cursor em `fcb.extra` e, no acesso direto, lê os blocos da corrente até o bloco desejado; ao estender, faz uma escrita extra no antigo último bloco. A FAT usa os mesmos blocos da encadeada, mas com os ponteiros em memória, então não tem acessos extras. A indexada usa blocos de índice de 1024 ponteiros, com índice de 2 níveis acima de 1024 blocos, e todo arquivo tem índice, mesmo vazio.

**Dificuldades:** VER SE TEVE ALGUMA 

### Integração ponta a ponta

**Onde:** `simes/integracao.py`, função `historico_para_requisicoes`.

**Decisões:** Cada item do histórico da CamadaBloco vira uma `Requisicao`. O histórico é ordenado por instante de chegada com `sorted`, que é estável, então os acessos de uma mesma operação mantêm a ordem. Os ids são numerados de 0 em diante depois da ordenação.

**Dificuldades:** O X12 leva cerca de 40 s, porque o SSTF percorre a fila inteira a cada escolha.

## 3. Experimentos

### X1 — Escalonadores sob quatro padrões de carga

**Hipótese:** [escrita ANTES de rodar o experimento]

**Fundamentação:** [por que esperavam isso; citem as seções do Silberschatz]

**Configuração:** [o que o experimento varia e o que mede]

**Resultados:** [tabela com os números principais e referência aos gráficos]

**Evidências:** [resultados/es.csv (experimento=X1); graficos/X1_resposta_media_ms.png]

**Análise:** [explicação dos resultados, inclusive o que contrariou a hipótese]

**Veredito:** [CONFIRMADA | PARCIALMENTE CONFIRMADA | REFUTADA]

### X2 — Polling × interrupção conforme o dispositivo

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X3 — Acesso sequencial × direto

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X4 — Custo de resolver caminhos conforme a profundidade

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X5 — Tabelas de arquivos abertos com vários processos

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X6 — Cache de blocos (M1)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X7 — Escalonadores avançados e inanição (M2)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X8 — DMA e buffering (M3)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X9 — Links e compartilhamento (M4)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X10 — Proteção e travas (M5)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X11 — Métodos de alocação (M6)

**Hipótese:** A contígua deve ter acesso direto barato, mas sofrer com fragmentação externa e com a cópia na realocação. A encadeada deve ser a pior no acesso direto, por precisar percorrer a corrente. A FAT deve corrigir isso com os ponteiros em memória. A indexada deve ficar no meio, com 1 ou 2 leituras de índice por acesso.

**Fundamentação:** Silberschatz, 9ª ed., seções 12.4 e 12.5.

**Configuração:** Mesma carga (`cargas/fs_alocacao.txt`, 2468 operações) e partição de 20.000 blocos, variando só o alocador.

**Resultados:**

| Alocador  | Erros | Acessos totais | Acessos/op | Tempo total (ms) |
|---|---|---|---|---|
| contígua  | 113   | 18.151         | 7,35       | 85.274           |
| encadeada | 0     | 191.309        | 77,5       | 31.413           |
| FAT       | 0     | 4.690          | 1,90       | 9.886            |
| indexada  | 0     | 10.585         | 4,29       | 35.345           |

**Evidências:** resultados/arquivos.csv (experimento=X11)

**Análise:** A contígua teve 113 falhas ENOSPC e 59 realocações, mesmo com 2.052 blocos livres, porque o espaço estava dividido em 50 trechos e o maior tinha 154 blocos (fragmentação externa). Como 113 operações falharam, ela fez menos trabalho útil que as outras, então a comparação não é totalmente justa. A encadeada teve o maior número de acessos (77,5 por operação), pelo custo da corrente no acesso direto. Mesmo assim, seu tempo total ficou menor que o da indexada. Uma explicação provável, que não verificamos, é que a CamadaBloco agrupa blocos consecutivos numa única requisição e a corrente ficou quase sequencial no disco pouco fragmentado. A FAT foi a melhor nos dois critérios, mas o custo em memória da tabela não aparece na simulação. A indexada ficou no meio e deixou cerca de 134 blocos a menos livres que a encadeada e a FAT, por causa dos blocos de índice.

**Veredito:** PARCIALMENTE CONFIRMADA

### X12 — Integração ponta a ponta

**Hipótese:** Uma alocação que gera mais acessos (a indexada, por causa dos blocos de índice) deve produzir mais requisições e mais movimento do braço do disco. A cache deve ajudar mais quando há reuso de blocos, e o escalonador deve reduzir o deslocamento.

**Fundamentação:** Silberschatz, 9ª ed., seções 10.4, 12.4 e 13.4.

**Configuração:** Cargas `compilador` e `banco_dados`, alocadores contígua e indexada, escalonadores FCFS, SSTF e SCAN, com e sem cache LRU de 1024 blocos em write-back.

**Resultados (FCFS):**

| Carga      | Alocador | Requisições | Deslocamento | Resposta sem cache (ms) | Com LRU: acerto / resposta (ms) |
|---|---|---|---|---|---|
| compilador | contígua | 5.400       | 6.900        | 4.971                   | 90,4% / 0,23 |
| compilador | indexada | 11.705      | 10.772       | 14.961                  | 95,7% / 0,17 |
| banco_dados| contígua | 3.610       | 360.570      | 6.159                   | 4,9% / 2.151 |
| banco_dados| indexada | 10.314      | 924.508      | 22.146                  | 74,5% / 765  |

**Evidências:** resultados/es.csv (experimento=X12)

**Análise:** A hipótese se confirmou quanto ao número de requisições (a indexada gerou de 2,2 a 2,9 vezes mais) e quanto ao efeito da cache, mas só em parte quanto ao deslocamento: com SSTF e SCAN no banco de dados, a indexada teve deslocamento menor que a contígua, e com cache o SCAN piorou o deslocamento em vez de reduzi-lo. Sem cache, a resposta média da indexada foi de 3 a 3,6 vezes maior. O SSTF reduziu muito o deslocamento (por exemplo, de 924.508 para 257 no banco de dados com indexada), mas a resposta média caiu bem menos, então menos deslocamento não garante menos tempo de resposta. A cache dependeu do padrão de acesso: no compilador o acerto passou de 90%, e no banco de dados com contígua foi só 4,9%. Com a indexada, o acerto subiu para 74,5%, provavelmente porque os blocos de índice são relidos várias vezes. Isso puxa a média para baixo com requisições baratas, então comparar a resposta média por requisição entre os alocadores engana. Observação a investigar: o SCAN com cache teve deslocamento muito maior que o SSTF (por exemplo, 49.996 contra 80 no compilador com contígua). Não confirmamos a causa. Este experimento comparou só contígua e indexada.

**Veredito:** PARCIALMENTE CONFIRMADA

### X13 — Armazenamento flash (bônus)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

## 4. Relação com sistemas reais

[Para cada tema do escopo, relacionem o que o simulador mostrou com o que Windows, Linux e
macOS fazem de fato. Exemplos: escalonadores de E/S do Linux (mq-deadline, BFQ, none); cache
de páginas e gravação periódica; cache de diretórios (dentry cache); FAT/exFAT nos pendrives;
estruturas do ext4, do NTFS e do APFS; travas mandatórias do Windows × consultivas do Linux.]

## 5. Limitações do simulador

[O que o modelo simplifica e como isso pode ter afetado as conclusões.]

## 6. Conclusões

[3 a 6 conclusões objetivas.]

## 7. Referências

- SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. *Operating System Concepts*. 9. ed. Wiley, 2013.
- [Outras fontes consultadas, com link]

## 8. Declaração de autoria e uso de IA

**Quem fez o quê:** [divisão do trabalho entre os integrantes]

**Uso de ferramentas de IA:**

| Ferramenta | Finalidade | Onde foi usada (arquivos ou seções) |
|---|---|---|
| [ex.: nenhuma] | [ ] | [ ] |
