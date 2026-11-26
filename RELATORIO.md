# Relatório — SimES: simulador de E/S e de sistema de arquivos

**Integrantes:** Eduardo Dieter Wachter, Joao Paulo Fritsch, Juliana Scapini Consoli, Julia Melo

**Repositório:** https://github.com/jsconsoli/SISOP_SimES

## 0. Resumo

Implementamos e avaliamos o núcleo do SimES, os módulos M1 (cache), M4 (links), M6 (alocação) e a integração ponta a ponta. A suíte executou 26 testes: 21 foram aprovados, cinco foram ignorados e não houve falhas. Nos experimentos, SSTF reduziu o tempo médio de resposta e o deslocamento total em relação ao FCFS nas quatro cargas do X1, embora a espera máxima não tenha diminuído em todas elas. No X6, a cache LRU chegou a 67,0% de acertos na carga com reuso. No X11, a FAT teve o menor custo de acesso medido; a alocação contígua sofreu 113 falhas por fragmentação externa. O X12 mostrou que cache e escalonamento podem reduzir muito o custo, mas os resultados dependem do padrão de acesso.

## 1. Escopo realizado

| Parte | Situação | Observação |
|---|---|---|
| N1 · Dispositivo (fornecido) | usado | HDD e dispositivo rápido usados nos experimentos do núcleo. |
| N2 · Subsistema de E/S (SSTF, SCAN, polling, interrupção) | completo | Implementados e avaliados em X1 e X2. |
| N3 · Sistema de arquivos | completo | Caminhos, operações de arquivo e tabelas de arquivos abertos cobertos por X3–X5. |
| N4 · Experimentos X1–X5 e relatório | completo | Resultados e gráficos em `resultados/` e `graficos/`. |
| M1 · Cache de blocos | completo | Cache LRU/FIFO, políticas de escrita e queda de energia; X6 executado. |
| M4 · Links e compartilhamento | completo | Hard links, links simbólicos e tratamento de ciclos; X9 executado. |
| M6 · Alocação em disco | completo | Encadeada, FAT e indexada; X11 executado. |
| Integração (grupos de 4) | completo | `historico_para_requisicoes` em `simes/integracao.py`; X12 executado. |
| Bônus flash | não feito | Fora do escopo escolhido. |

Resultado dos testes automáticos (`python3 executar.py testes`): **26 testes no total: 21 aprovados, 5 ignorados e nenhuma falha** (`OK (skipped=5)`).

## 2. Implementação

### N2 — Subsistema de E/S

**Onde:** `simes/es/escalonadores.py` (`SSTF`, `SCAN` e fábrica de escalonadores), `simes/es/cpu.py` (`custo_cpu`) e `simes/es/simulador.py`.

**Decisões:** SSTF escolhe a requisição pendente mais próxima da cabeça. SCAN mantém a direção de movimento e a inverte quando não há requisições à frente. O custo de CPU modela polling e interrupção separadamente; o simulador processa as requisições pelos eventos de chegada e conclusão. Nos testes de livro, os casos de SCAN para as duas direções e SSTF passam.

**Dificuldades:** O comportamento do escalonador depende da fila no instante de cada escolha. Na integração, o SSTF reavalia a fila inteira a cada seleção, o que aumenta o tempo de execução do X12.

### N3 — Sistema de arquivos

**Onde:** `simes/arquivos/sistema.py`, principalmente `resolver`, `_descer`, `_pai`, `open`, `read`, `write`, `seek`, `close` e `unlink`; estruturas e tabelas ficam em `simes/arquivos/estruturas.py`.

**Decisões:** A resolução percorre os componentes do caminho a partir da raiz e contabiliza os acessos aos diretórios. O sistema mantém uma tabela global de arquivos abertos e associa handles de processo a entradas compartilhadas, com contador de aberturas. Leitura e escrita atualizam a posição do handle; `seek` permite acesso direto. Um arquivo removido com handles ativos permanece utilizável e só tem seus blocos liberados quando a última referência é fechada.

**Dificuldades:** Foi necessário manter coerentes as referências compartilhadas entre processos e distinguir a remoção do nome no diretório da liberação efetiva dos dados. Os testes cobrem abertura compartilhada e `unlink` com arquivo aberto.

### M1 — Cache de blocos

**Onde:** `simes/es/cache.py` (`Cache`, `CacheLRU`, `CacheFIFO` e `criar_cache`).

**Decisões:** LRU atualiza a recência quando um bloco é usado; FIFO mantém a ordem de entrada. Write-through envia as escritas ao dispositivo imediatamente; write-back mantém blocos sujos e os descarrega posteriormente. A simulação de queda contabiliza os blocos sujos que ainda não foram persistidos.

**Dificuldades:** A avaliação precisa separar acertos de leitura/escrita, escritas físicas e dados ainda sujos no momento da queda, porque uma taxa de acerto maior não garante menor resposta em todas as métricas.

### M4 — Links e compartilhamento

**Onde:** `simes/arquivos/sistema.py` (`link`, `symlink`, `resolver` e `percorrer`) e `simes/arquivos/estruturas.py`.

**Decisões:** Hard links compartilham o mesmo FCB e contam referências; links simbólicos armazenam um caminho de destino, que pode ser seguido durante a resolução. O percurso limita e identifica ciclos, e preserva erros como destino inexistente e permissão negada.

**Dificuldades:** Links simbólicos podem formar ciclos ou apontar para nomes removidos; a resolução precisa detectar os ciclos sem confundi-los com caminhos apenas inexistentes.

### M6 — Alocação em disco

**Onde:** `simes/arquivos/alocacao.py` (`AlocadorContiguo`, `AlocadorEncadeado`, `AlocadorFAT` e `AlocadorIndexado`).

**Decisões:** A encadeada guarda um cursor em `fcb.extra` e, no acesso direto, percorre a corrente até o bloco desejado; ao estender, faz uma escrita extra no antigo último bloco. A FAT usa os mesmos blocos da encadeada, mas mantém os ponteiros em memória. A indexada usa blocos de índice com 1024 ponteiros, adiciona um nível acima de 1024 blocos e mantém índice mesmo para arquivo vazio.

**Dificuldades:** A contígua exige realocação quando não há espaço adjacente, e a fragmentação externa pode impedir uma alocação mesmo com blocos livres suficientes no total. Na indexada, blocos de índice consomem espaço e acessos; na encadeada, o acesso direto percorre a cadeia.

### Integração ponta a ponta

**Onde:** `simes/integracao.py`, função `historico_para_requisicoes`.

**Decisões:** Cada item do histórico da CamadaBloco vira uma `Requisicao`. O histórico é ordenado por instante de chegada com `sorted`, que é estável, então os acessos de uma mesma operação mantêm a ordem. Os ids são numerados de 0 em diante depois da ordenação.

**Dificuldades:** O X12 leva cerca de 28 s nesta execução. O SSTF percorre a fila inteira a cada escolha; o experimento gera milhares de requisições.

## 3. Experimentos

### X1 — Escalonadores sob quatro padrões de carga

**Hipótese:** SSTF deve reduzir deslocamento e resposta média em relação ao FCFS, pois seleciona o pedido mais próximo. SCAN deve oferecer espera mais previsível ao varrer o disco, embora possa percorrer cilindros sem pedidos. Sob rajadas, nenhum escalonador deve eliminar a fila causada pela sobrecarga.

**Fundamentação:** Silberschatz, 9ª ed., seção 10.4, “Disk Scheduling”: FCFS preserva ordem de chegada; SSTF prioriza proximidade e pode causar inanição; SCAN percorre o disco alternando a direção.

**Configuração:** Cargas sequencial, aleatória, concentrada e em rajadas; 2.000 requisições em cada carga; FCFS, SSTF e SCAN em HDD, com interrupção. Medimos resposta média, espera máxima e deslocamento total.

**Resultados:** Resposta média em milissegundos; valores em cada célula seguem FCFS / SSTF / SCAN.

| Carga | FCFS | SSTF | SCAN |
|---|---:|---:|---:|
| Sequencial | 10.241,05 | 17,39 | 23,21 |
| Aleatória | 50,10 | 20,99 | 31,53 |
| Concentrada | 19,80 | 15,02 | 33,20 |
| Rajadas | 266,97 | 147,49 | 148,62 |

Na carga em rajadas, a espera máxima foi 597,29 ms no FCFS, 296,99 ms no SSTF e 285,44 ms no SCAN. Os gráficos de resposta, espera e deslocamento estão em `graficos/X1_resposta_media_ms.svg`, `graficos/X1_espera_max_ms.svg` e `graficos/X1_deslocamento_total.svg`.

**Evidências:** `resultados/es.csv` (experimento=X1); `graficos/X1_resposta_media_ms.svg`; `graficos/X1_espera_max_ms.svg`; `graficos/X1_deslocamento_total.svg`.

**Análise:** SSTF teve a menor resposta média e reduziu o deslocamento total nas quatro cargas em relação ao FCFS: de 7.184.093 para 2.336.365 cilindros na sequencial (67,5%); de 3.316.472 para 2.631.714 na aleatória (20,6%); de 1.864.164 para 1.613.030 na concentrada (13,5%); e de 3.341.490 para 209.811 em rajadas (93,7%). SCAN teve o menor deslocamento em rajadas, mas não a menor resposta média. Na carga concentrada, a espera máxima de SSTF (130,52 ms) ficou acima de FCFS (96,02 ms), mostrando que a média menor não garante justiça para cada requisição. Os resultados apoiam a vantagem de proximidade, mas não medem diretamente inanição em uma carga ilimitada.

**Veredito:** PARCIALMENTE CONFIRMADA

### X2 — Polling × interrupção conforme o dispositivo

**Hipótese:** Polling deve consumir mais CPU quando o dispositivo é lento, porque a CPU fica verificando a conclusão; em dispositivos rápidos o custo da interrupção pode se aproximar ou até superar o polling.

**Fundamentação:** Silberschatz, 9ª ed., capítulo 13, “I/O Systems”, seções sobre hardware de E/S, polling e interrupções. Polling mantém a CPU consultando o dispositivo; interrupções permitem que a CPU execute outras tarefas enquanto aguarda o evento.

**Configuração:** HDD e dispositivo rápido; cargas aleatória e sequencial; 2.000 requisições; FCFS e comparação entre polling e interrupção. Medimos a fração do tempo de CPU atribuída à E/S e também a resposta média.

**Resultados:** Na carga aleatória, CPU de E/S foi 86,28% com polling e 1,12% com interrupção no HDD; no dispositivo rápido foi 0,53% e 1,12%, respectivamente. Na sequencial, os valores foram 100,00% e 0,84% no HDD, e 1,07% e 2,28% no dispositivo rápido. O tempo de resposta se manteve igual entre os modos para cada dispositivo e carga.

**Evidências:** `resultados/es.csv` (experimento=X2); `graficos/X2_cpu.svg`.

**Análise:** No HDD, a interrupção reduziu muito a ocupação da CPU sem alterar a resposta modelada. No dispositivo rápido, a interrupção teve custo de CPU maior que o polling, compatível com o custo fixo de tratar interrupções quando a operação é muito curta. A hipótese se confirma para o HDD e parcialmente para o dispositivo rápido.

**Veredito:** PARCIALMENTE CONFIRMADA

### X3 — Acesso sequencial × direto

**Hipótese:** A carga de banco de dados, com operações de acesso direto, deve gerar mais operações de arquivo e custo total maior que a carga sequencial do compilador; as operações de seek em si não precisam acessar blocos.

**Fundamentação:** Silberschatz, 9ª ed., seção 11.2, “Access Methods”: acesso sequencial percorre registros em ordem; acesso direto permite posicionar-se em blocos ou registros específicos.

**Configuração:** Cargas `fs_compilador.txt` e `fs_banco_dados.txt`, alocação contígua, sistema padrão e comparação do total de operações, acessos a blocos e tempos médios.

**Resultados:** Compilador: 3.904 operações, zero erros, 1,38 acessos por operação e 3,07 ms por operação. Banco de dados: 6.602 operações, zero erros, 0,55 acessos por operação e 3,01 ms por operação. O tempo total foi 11.986,65 ms e 19.846,96 ms, respectivamente. O banco de dados executou 3.000 seeks, que não geraram acessos a blocos.

**Evidências:** `resultados/arquivos.csv` e `resultados/arquivos_por_operacao.csv` (experimento=X3); `graficos/X3_tempo_por_operacao.svg`.

**Análise:** A carga de banco de dados teve mais operações e maior tempo total, mas menos acessos médios por operação porque os seeks não leem blocos. Assim, a diferença agregada decorre da composição e do volume das operações, não de um custo alto de seek no modelo.

**Veredito:** PARCIALMENTE CONFIRMADA

### X4 — Custo de resolver caminhos conforme a profundidade

**Hipótese:** O custo de `open` deve crescer com a quantidade de diretórios no caminho, pois é preciso resolver cada componente antes de alcançar o arquivo.

**Fundamentação:** Silberschatz, 9ª ed., seção 11.3, “Directory Structure”, sobre caminhos e busca de componentes em diretórios.

**Configuração:** Cargas geradas para profundidades de 1 a 10 diretórios, 20 operações de `open` por profundidade, sistema de arquivos contíguo. Medimos acessos e tempo médio por `open`.

**Resultados:** Os acessos médios cresceram de 2 para 11 por abertura; o tempo médio cresceu de 4,25 ms para 4,61 ms. Cada nível acrescentou um acesso e 0,04 ms no modelo.

**Evidências:** `resultados/arquivos_por_operacao.csv` (experimento=X4); `graficos/X4_open_por_profundidade.svg`.

**Análise:** O crescimento foi linear nos acessos e no custo temporal, como esperado. A pequena variação de tempo por nível reflete os custos fixos e unitários definidos pelo simulador, não medições de um sistema real.

**Veredito:** CONFIRMADA

### X5 — Tabelas de arquivos abertos com vários processos

**Hipótese:** Processos que abrem um mesmo arquivo podem compartilhar uma entrada global e manter handles próprios; assim, o número de entradas globais pode ser menor que a soma das entradas nas tabelas dos processos.

**Fundamentação:** Silberschatz, 9ª ed., seção 11.1, “File Concept”, sobre arquivos abertos, descritores por processo e estruturas globais de controle.

**Configuração:** Carga `fs_servidor_web.txt`, sistema contíguo e bloqueio consultivo. Medimos os máximos das tabelas global e por processo e o contador de aberturas.

**Resultados:** Foram executadas 6.279 operações sem erros. Máximo de 12 entradas globais, 3 por processo e 24 somadas nas tabelas de processo; o maior contador de aberturas foi 6.

**Evidências:** `resultados/arquivos.csv` (experimento=X5); `graficos/X5_tabelas.svg`.

**Análise:** A carga exercitou handles simultâneos em mais de um processo e contadores de referências. A soma máxima por processo superou a tabela global, consistente com compartilhamento de entradas globais. Os máximos são picos da carga, não médias.

**Veredito:** CONFIRMADA

### X6 — Cache de blocos (M1)

**Hipótese:** Aumentar a capacidade da cache deve elevar a taxa de acertos em uma carga com reuso. Write-back deve reduzir escritas físicas e resposta, ao custo de poder perder dados sujos em uma queda; LRU e FIFO podem diferir conforme a sequência de acessos.

**Fundamentação:** Silberschatz, 9ª ed., seção 12.6, “Efficiency and Performance”, sobre cache de buffer e políticas de escrita; seção 12.7, “Recovery”, para persistência e recuperação.

**Configuração:** Carga `es_reuso.txt`, 3.000 requisições, HDD, FCFS e interrupção. LRU e FIFO com capacidades de 64, 128, 256, 512, 1.024 e 2.048 blocos; write-through e write-back. Também foi simulada uma queda no meio da carga.

**Resultados:** Com LRU write-back, a taxa de acerto aumentou de 39,64% (64 blocos) para 67,01% (1.024 blocos), sem ganho adicional em 2.048. As escritas físicas caíram de 1.045 no write-through para 541 em write-back a partir de capacidade 512. Na queda, write-through não perdeu blocos sujos; write-back perdeu de 28 a 55 blocos nas capacidades avaliadas. A melhor resposta LRU write-back foi 23,36 ms em 64 blocos; respostas maiores nas capacidades intermediárias mostram que taxa de acerto não determina sozinha a média.

**Evidências:** `resultados/es.csv` (experimento=X6); `graficos/X6_acerto.svg`; `graficos/X6_acerto_fifo.svg`; `graficos/X6_escrita.svg`.

**Análise:** A tendência de mais capacidade elevar acertos se confirmou até o conjunto de trabalho da carga, com saturação em 1.024 blocos. Write-back reduziu as escritas físicas, mas os blocos sujos ainda em cache foram contabilizados como perdidos na queda. LRU teve mais acertos que FIFO em capacidades pequenas nesta carga; a diferença diminuiu em capacidades maiores. O tempo de resposta oscilou com a ordem das requisições e do escalonamento, portanto não variou monotonicamente com a capacidade.

**Veredito:** PARCIALMENTE CONFIRMADA

### X9 — Links e compartilhamento (M4)

**Hipótese:** Hard links devem compartilhar os dados do mesmo arquivo; links simbólicos devem resolver caminhos válidos e a implementação deve detectar ciclos e destinos removidos.

**Fundamentação:** Silberschatz, 9ª ed., seção 11.3, “Directory Structure”, sobre estrutura de diretórios e links; a resolução de links exige percorrer componentes e tratar referências inválidas.

**Configuração:** Carga `fs_links.txt`, alocação contígua e bloqueio consultivo; analisamos operações concluídas e contadores de erros, ciclos e links pendentes.

**Resultados:** 56 operações, 3 erros e 258 acessos a blocos. Foram detectados 11 ciclos; a carga registrou um `ELOOP`, um `ENOENT`, um `EPERM` e três links pendentes.

**Evidências:** `resultados/arquivos.csv` (experimento=X9); `cargas/fs_links.txt`.

**Análise:** A carga alcançou os casos previstos de links, ciclos, destino inexistente e permissão negada. Os erros observados fazem parte dos cenários provocados pela carga, não indicam falha automática no experimento. Os contadores confirmam a detecção, mas não medem o custo de links em sistemas reais.

**Veredito:** CONFIRMADA

### X11 — Métodos de alocação (M6)

**Hipótese:** A contígua deve ter acesso direto barato, mas sofrer com fragmentação externa e cópia na realocação. A encadeada deve ser a pior no acesso direto, por percorrer a corrente. A FAT deve reduzir esse custo com ponteiros em memória. A indexada deve ficar entre as duas, com uma ou duas leituras de índice por acesso.

**Fundamentação:** Silberschatz, 9ª ed., seções 12.4, “Allocation Methods”, e 12.5, “Free-Space Management”.

**Configuração:** Mesma carga (`cargas/fs_alocacao.txt`, 2.468 operações) e partição de 20.000 blocos, variando apenas o alocador. Medimos erros, acessos totais, acessos por operação e tempo.

**Resultados:**

| Alocador | Erros | Acessos totais | Acessos/op | Tempo total (ms) |
|---|---:|---:|---:|---:|
| Contígua | 113 | 18.151 | 7,35 | 85.273,67 |
| Encadeada | 0 | 191.309 | 77,52 | 31.412,71 |
| FAT | 0 | 4.690 | 1,90 | 9.886,22 |
| Indexada | 0 | 10.585 | 4,29 | 35.345,40 |

**Evidências:** `resultados/arquivos.csv` (experimento=X11); `graficos/X11_alocacao.svg`; `graficos/X11_fragmentacao.svg`.

**Análise:** A contígua teve 113 falhas `ENOSPC` e 59 realocações, mesmo com 2.052 blocos livres: o espaço estava dividido em 50 trechos e o maior tinha 154 blocos, evidência de fragmentação externa. Como houve menos trabalho útil nas execuções contíguas, a comparação de tempo não é totalmente equivalente. A encadeada teve mais acessos, pelo percurso no acesso direto. A FAT teve o menor custo medido, mas o espaço de memória ocupado pela tabela não aparece na simulação. A indexada ficou entre FAT e encadeada em acessos e usou blocos de índice adicionais. O tempo total menor da encadeada que da indexada pode decorrer do agrupamento de blocos consecutivos pela CamadaBloco; não isolamos essa causa.

**Veredito:** PARCIALMENTE CONFIRMADA

### X12 — Integração ponta a ponta

**Hipótese:** Uma alocação que gera mais acessos, como a indexada por causa dos blocos de índice, deve produzir mais requisições e movimento do braço. Cache deve ajudar mais quando há reuso de blocos, e escalonadores que aproximam acessos devem reduzir o deslocamento.

**Fundamentação:** Silberschatz, 9ª ed., seções 10.4, 12.4 e 12.6: escalonamento de disco, métodos de alocação e eficiência de cache.

**Configuração:** Cargas `compilador` e `banco_dados`, alocadores contígua e indexada, escalonadores FCFS, SSTF e SCAN, com e sem cache LRU de 1.024 blocos em write-back. As operações do sistema de arquivos foram convertidas em requisições de E/S e executadas no HDD.

**Resultados:** Valores FCFS sem cache e com cache LRU, respectivamente.

| Carga e alocador | Requisições | Deslocamento sem/com cache | Resposta média sem/com cache (ms) | Acerto da cache |
|---|---:|---:|---:|---:|
| Compilador, contígua | 5.400 | 6.900 / 104 | 4.970,86 / 0,23 | 90,4% |
| Compilador, indexada | 11.705 | 10.772 / 116 | 14.961,01 / 0,17 | 95,7% |
| Banco de dados, contígua | 3.610 | 360.570 / 260.926 | 6.158,75 / 2.151,29 | 4,9% |
| Banco de dados, indexada | 10.314 | 924.508 / 263.584 | 22.146,10 / 765,05 | 74,5% |

**Evidências:** `resultados/es.csv` (experimento=X12); `graficos/X12_resposta.svg`.

**Análise:** A indexada gerou 2,2 a 2,9 vezes mais requisições que a contígua. A cache reduziu muito a resposta média no compilador e no banco de dados com alocação indexada, onde blocos de índice são reutilizados; ajudou menos no banco de dados contíguo, cuja taxa de acerto foi 4,9%. SSTF reduziu o deslocamento em várias configurações, mas com cache o SCAN aumentou o deslocamento em relação ao SSTF e, em alguns casos, ao FCFS. Menos deslocamento também não garante por si só menor tempo de resposta, pois há fila, custo de serviço e hits de cache. O experimento apoia a hipótese sobre volume de requisições e reuso, mas mostra que movimento e resposta dependem da combinação entre carga, alocador, cache e escalonador.

**Veredito:** PARCIALMENTE CONFIRMADA

## 4. Relação com sistemas reais

O SimES abstrai o escalonamento em uma fila única e em HDD. O Linux usa a camada multi-queue blk-mq e pode oferecer políticas como `mq-deadline`, `bfq` e `none`, selecionáveis conforme o dispositivo e o sistema. BFQ considera compartilhamento proporcional e responsividade; esse objetivo de justiça não aparece na métrica isolada de deslocamento do SimES. [Documentação do blk-mq](https://docs.kernel.org/6.11/block/blk-mq.html), [seleção de escalonador](https://docs.kernel.org/6.2/block/switching-sched.html) e [BFQ](https://docs.kernel.org/block/bfq-iosched.html).

O write-back do X6 representa uma simplificação do cache de arquivos real. O Windows mantém cache de dados de arquivos e grava páginas alteradas posteriormente; também oferece opções para solicitar escrita imediata. O modelo do trabalho reduz isso a capacidade, política e uma queda em instante fixo, sem temporizadores adaptativos nem recuperação. [Microsoft Learn — File Caching](https://learn.microsoft.com/en-us/windows/win32/fileio/file-caching).

A carga de diretórios do X4 mostra o custo de percorrer componentes de um caminho. Sistemas reais mantêm estruturas em memória e caches de nomes/metadados, então aberturas repetidas podem não repetir todos os acessos físicos simulados. Os métodos de alocação do X11 ajudam a entender compromissos de contiguidade, tabela e índice, mas não reproduzem integralmente ext4, NTFS ou APFS. O APFS, sistema padrão das versões modernas do macOS, é projetado para armazenamento flash e inclui copy-on-write, snapshots, criptografia e compartilhamento de espaço; por isso não corresponde a um único dos alocadores modelados. [Apple — APFS](https://support.apple.com/en-asia/guide/security/seca6147599e/web).

A FAT da simulação é uma tabela em memória e não representa todos os detalhes de FAT/exFAT em mídias removíveis. As métricas de X9 também não representam todas as regras de permissões, recuperação e concorrência de Windows, Linux ou macOS; servem para estudar a semântica simplificada de nomes, referências e caminhos.

## 5. Limitações do simulador

- O HDD usa custos determinísticos e não representa firmware, cache interno, filas do controlador, setores defeituosos ou variação física. O dispositivo rápido também é uma abstração.
- O simulador não mede tempo de CPU real, latência do sistema operacional ou concorrência real; os valores são consequências das constantes e regras do modelo.
- A fila única ignora múltiplas filas de hardware e a paralelização de SSDs. SSTF pode parecer especialmente vantajoso para movimento sem capturar toda a questão de justiça.
- A cache não modela memória virtual, read-ahead, writeback periódico, barreiras, journaling ou garantias de durabilidade de sistemas reais. O cenário de queda é um evento simplificado.
- Os custos de caminhos, handles, links e alocadores são contagens definidas pela implementação. Não equivalem a benchmarks de ext4, NTFS, APFS ou exFAT.
- No X11, contígua teve operações que falharam por fragmentação, então seu tempo não cobre exatamente o mesmo trabalho útil que os demais métodos. No X12, a resposta média por requisição mistura acessos baratos de cache e requisições físicas.
- Os dados são de uma execução determinística de cada configuração; não há intervalos de confiança nem variação de sementes para estimar dispersão.

## 6. Conclusões

1. Nos padrões avaliados, SSTF reduziu a resposta média frente ao FCFS, mas a espera máxima pode permanecer alta para alguns pedidos.
2. Interrupções pouparam CPU no HDD; no dispositivo rápido, seu custo fixo foi maior que o polling em duas cargas.
3. A cache com reuso elevou acertos e write-back reduziu escritas físicas, mas deixou dados sujos vulneráveis à queda simulada.
4. A alocação contígua falhou mesmo com espaço total livre por fragmentação externa; FAT teve menor custo de acesso no modelo.
5. Na integração, cache e padrão de acesso mudaram substancialmente os resultados; não há um melhor escalonador ou alocador para todas as métricas.

## 7. Referências

- SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. *Operating System Concepts*. 9. ed. Wiley, 2013.
- Linux Kernel Documentation. [Multi-Queue Block IO Queueing Mechanism (blk-mq)](https://docs.kernel.org/6.11/block/blk-mq.html); [Switching Scheduler](https://docs.kernel.org/6.2/block/switching-sched.html); [BFQ](https://docs.kernel.org/block/bfq-iosched.html).
- Microsoft Learn. [File Caching](https://learn.microsoft.com/en-us/windows/win32/fileio/file-caching).
- Apple Support. [Role of Apple File System](https://support.apple.com/en-asia/guide/security/seca6147599e/web).

## 8. Declaração de autoria e uso de IA

**Quem fez o quê:** O desenvolvimento do projeto foi realizado de forma colaborativa entre os quatro integrantes, com a seguinte divisão de responsabilidades:

- **Eduardo Dieter Wachter:** revisão e validação do módulo M1 (cache de blocos), relacionado ao experimento X6.
- **Joao Paulo Fritsch:** implementação do núcleo N2 (escalonadores e CPU) e da maior parte do núcleo N3 (sistema de arquivos), relacionados aos experimentos X1 a X5.
- **Juliana Scapini Consoli:** implementação dos módulos M4 (links e compartilhamento) e M6 (métodos de alocação), além de ajustes pontuais no núcleo N3. Suas contribuições estão relacionadas principalmente aos experimentos X9 e X11.
- **Julia Melo:** desenvolvimento da integração entre o sistema de arquivos e o subsistema de E/S, relacionada ao experimento X12.

Embora as responsabilidades tenham sido distribuídas, o desenvolvimento foi realizado de maneira colaborativa, com participação do grupo nas etapas de testes, revisão e documentação.

**Uso de ferramentas de IA:**

| Ferramenta | Finalidade | Onde foi usada (arquivos ou seções) |
|---|---|---|
| ChatGPT Codex | Executar testes e experimentos, gerar gráficos SVG equivalentes sem dependência de matplotlib e apoiar a redação e revisão do relatório. | `graficos_svg.py`, `graficos/`, `RELATORIO.md` |
