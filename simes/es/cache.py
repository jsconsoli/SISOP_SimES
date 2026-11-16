# -*- coding: utf-8 -*-
"""
Módulo M1 — cache de blocos (buffer cache).

Referência: Silberschatz, 9ª ed., 13.4.3 (Caching) e 12.6 (Efficiency and Performance) — pesquisa.

Implementem CacheLRU e CacheFIFO com a interface abaixo. O simulador de E/S chama:

    ler(bloco) -> bool
        True se o bloco está na cache (acerto). Num acerto, a LRU atualiza a recência;
        a FIFO não muda nada.
    inserir(bloco) -> list[int]
        Chamado depois de uma falta de leitura, quando o bloco chega do disco. Se a cache
        estiver cheia, expulsa uma vítima (LRU: a usada há mais tempo; FIFO: a que entrou
        primeiro). Devolve os blocos SUJOS expulsos, que o simulador vai gravar no disco.
    escrever(bloco) -> list[int]
        Escrita do usuário. Coloca (ou atualiza) o bloco na cache e devolve a lista de blocos
        que precisam ser gravados no disco AGORA:
          write-through: o próprio bloco (+ sujos expulsos, que não existem nesta política);
          write-back:    só os blocos sujos expulsos; o bloco escrito fica marcado como sujo.
        Uma escrita conta como acesso para a LRU.
    sincronizar() -> list[int]
        Gravação periódica (a cada INTERVALO_SYNC_MS): devolve todos os blocos sujos e os
        marca como limpos.
    sujos() -> int
        Quantos blocos estão sujos agora (usado para medir a perda numa queda de energia).

Política de escrita: 'write-through' ou 'write-back'.
"""

from collections import OrderedDict


class Cache:
    nome = "?"
    atualiza_recencia = False

    def __init__(self, capacidade, escrita="write-back"):
        if escrita not in ("write-through", "write-back"):
            raise ValueError("escrita deve ser 'write-through' ou 'write-back'")
        if isinstance(capacidade, bool) or not isinstance(capacidade, int) or capacidade <= 0:
            raise ValueError("capacidade deve ser um inteiro positivo")
        self.capacidade = capacidade
        self.escrita = escrita
        # A ordem é do bloco mais antigo para o mais recente. No FIFO, hits não
        # alteram essa ordem; no LRU, os métodos públicos movem o bloco ao fim.
        self._blocos = OrderedDict()

    def _tocar(self, bloco):
        if self.atualiza_recencia:
            self._blocos.move_to_end(bloco)

    def _inserir(self, bloco, sujo=False):
        """Insere/atualiza um bloco e devolve os blocos sujos expulsos."""
        if bloco in self._blocos:
            if sujo:
                self._blocos[bloco] = True
            self._tocar(bloco)
            return []

        expulsos = []
        if len(self._blocos) >= self.capacidade:
            vitima, estava_sujo = self._blocos.popitem(last=False)
            if estava_sujo:
                expulsos.append(vitima)
        self._blocos[bloco] = bool(sujo)
        return expulsos

    def ler(self, bloco):
        if bloco not in self._blocos:
            return False
        self._tocar(bloco)
        return True

    def inserir(self, bloco):
        return self._inserir(bloco)

    def escrever(self, bloco):
        sujo = self.escrita == "write-back"
        expulsos = self._inserir(bloco, sujo=sujo)
        if self.escrita == "write-through":
            # A escrita do usuário precisa chegar ao disco imediatamente.
            return [bloco] + expulsos
        return expulsos

    def sincronizar(self):
        if self.escrita == "write-through":
            return []
        sujos = []
        for bloco in self._blocos:
            if self._blocos[bloco]:
                sujos.append(bloco)
                self._blocos[bloco] = False
        return sujos

    def sujos(self):
        return sum(self._blocos.values())


class CacheLRU(Cache):
    nome = "LRU"
    atualiza_recencia = True

    def __init__(self, capacidade, escrita="write-back"):
        super().__init__(capacidade, escrita)


class CacheFIFO(Cache):
    nome = "FIFO"

    def __init__(self, capacidade, escrita="write-back"):
        super().__init__(capacidade, escrita)


CACHES = {"LRU": CacheLRU, "FIFO": CacheFIFO}


def criar_cache(nome, capacidade, escrita):
    try:
        return CACHES[nome](capacidade, escrita)
    except KeyError:
        raise ValueError("cache desconhecida: %s" % nome)
