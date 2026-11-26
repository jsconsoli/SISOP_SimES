# -*- coding: utf-8 -*-
"""
Integração ponta a ponta (obrigatória para grupos de 4 integrantes).

Ideia: rodar uma carga do SISTEMA DE ARQUIVOS guardando o histórico dos acessos ao disco
(CamadaBloco com guardar_historico=True) e transformar esse histórico numa carga de E/S, que
então passa pela cache (M1) e pelo escalonador, no simulador de E/S. Assim dá para medir
como a organização dos arquivos no disco (alocação, diretórios) afeta o escalonamento e a
cache.

Cada item do histórico é (instante_ms, processo, tipo, bloco, n_blocos).
"""
from simes.es.requisicao import Requisicao

#Requisicao. Esta função faz a tradução, ligando as duas camadas (experimento X12).

def historico_para_requisicoes(historico):
      
    # sorted() é estável: acessos do mesmo instante (mesma operação) mantêm a ordem original.
    ordenado = sorted(historico, key=lambda item: item[0])
    return [Requisicao(i, instante, processo, tipo, bloco, n_blocos)
            for i, (instante, processo, tipo, bloco, n_blocos) in enumerate(ordenado)]