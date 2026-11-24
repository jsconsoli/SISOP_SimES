# -*- coding: utf-8 -*-
"""Gera os gráficos dos experimentos em SVG usando apenas a biblioteca padrão."""
import csv
import html
import os
from collections import OrderedDict

BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, "resultados")
OUT = os.path.join(BASE, "graficos")
W, H = 900, 500
CORES = ["#2563eb", "#f97316", "#16a34a", "#9333ea", "#0891b2", "#dc2626", "#64748b"]


def ler(arq):
    with open(os.path.join(RES, arq), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def n(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


def svg_inicio(titulo, subtitulo=""):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
            '<rect width="100%" height="100%" fill="white"/>',
            f'<text x="{W/2}" y="34" text-anchor="middle" font-family="Arial" font-size="21" font-weight="bold">{html.escape(titulo)}</text>',
            f'<text x="{W/2}" y="58" text-anchor="middle" font-family="Arial" font-size="12" fill="#475569">{html.escape(subtitulo)}</text>']


def escreve(nome, partes):
    partes.append("</svg>")
    with open(os.path.join(OUT, nome), "w", encoding="utf-8") as f:
        f.write("\n".join(partes))


def barras(nome, titulo, grupos, series, valores, eixo, log=False):
    p = svg_inicio(titulo, eixo + (" (escala logarítmica)" if log else ""))
    left, right, top, bottom = 75, 25, 90, 105
    pw, ph = W-left-right, H-top-bottom
    todos = [v for v in valores.values() if v > 0]
    vmax = max(todos or [1])
    vmin = min(todos or [1])
    if log:
        import math
        lo = math.log10(max(vmin, 1e-6)); hi = math.log10(max(vmax, vmin*1.01))
        scale = lambda v: (math.log10(max(v, 1e-6))-lo)/(hi-lo or 1)
        ticks = [10**(lo+(hi-lo)*i/4) for i in range(5)]
    else:
        hi = vmax * 1.08 or 1
        scale = lambda v: v/hi
        ticks = [hi*i/4 for i in range(5)]
    for i, t in enumerate(ticks):
        y = top + ph*(1-i/4)
        p += [f'<line x1="{left}" y1="{y:.1f}" x2="{W-right}" y2="{y:.1f}" stroke="#e2e8f0"/>',
              f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-family="Arial" font-size="11" fill="#475569">{t:.3g}</text>']
    slot = pw/max(1,len(grupos)); bw = min(40, slot*.72/max(1,len(series)))
    for gi,g in enumerate(grupos):
        center=left+slot*(gi+.5)
        for si,s in enumerate(series):
            v=valores.get((g,s),0); bh=ph*scale(v)
            x=center-(bw*len(series))/2+si*bw; y=top+ph-bh
            p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-2:.1f}" height="{bh:.1f}" fill="{CORES[si%len(CORES)]}"/>')
        label=html.escape(str(g))
        p.append(f'<text x="{center:.1f}" y="{top+ph+20}" text-anchor="middle" font-family="Arial" font-size="11" fill="#334155">{label}</text>')
    lx=left
    for i,s in enumerate(series):
        p += [f'<rect x="{lx}" y="{H-40}" width="12" height="12" fill="{CORES[i%len(CORES)]}"/>',
              f'<text x="{lx+17}" y="{H-30}" font-family="Arial" font-size="11" fill="#334155">{html.escape(str(s))}</text>']
        lx += 40+min(150, len(str(s))*7)
    escreve(nome,p)


def linhas(nome,titulo,series_xy,xlabel,ylabel):
    p=svg_inicio(titulo,ylabel); left,right,top,bottom=75,25,90,105; pw,ph=W-left-right,H-top-bottom
    xs=[x for pts in series_xy.values() for x,y in pts]; ys=[y for pts in series_xy.values() for x,y in pts]
    xmin,xmax=min(xs or [0]),max(xs or [1]); ymin,ymax=0,max(ys or [1])*1.08 or 1
    for i in range(5):
        y=top+ph*(1-i/4); v=ymax*i/4
        p += [f'<line x1="{left}" y1="{y:.1f}" x2="{W-right}" y2="{y:.1f}" stroke="#e2e8f0"/>',
              f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-family="Arial" font-size="11" fill="#475569">{v:.3g}</text>']
    for i in range(5):
        x=left+pw*i/4; v=xmin+(xmax-xmin)*i/4
        p.append(f'<text x="{x:.1f}" y="{top+ph+20}" text-anchor="middle" font-family="Arial" font-size="11" fill="#475569">{v:g}</text>')
    for si,(name,pts) in enumerate(series_xy.items()):
        pts=sorted(pts); coords=[(left+(x-xmin)/(xmax-xmin or 1)*pw,top+ph-y/(ymax or 1)*ph) for x,y in pts]
        p.append('<polyline fill="none" stroke="%s" stroke-width="2.5" points="%s"/>'%(CORES[si%len(CORES)]," ".join('%.1f,%.1f'%q for q in coords)))
        for x,y in coords:p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{CORES[si%len(CORES)]}"/>')
        p += [f'<line x1="{left+si*170}" y1="{H-40}" x2="{left+si*170+18}" y2="{H-40}" stroke="{CORES[si%len(CORES)]}" stroke-width="3"/>',
              f'<text x="{left+si*170+24}" y="{H-36}" font-family="Arial" font-size="11">{html.escape(name)}</text>']
    p += [f'<text x="{W/2}" y="{H-8}" text-anchor="middle" font-family="Arial" font-size="12">{html.escape(xlabel)}</text>']
    escreve(nome,p)


def main():
    os.makedirs(OUT,exist_ok=True)
    es,fs,po=ler("es.csv"),ler("arquivos.csv"),ler("arquivos_por_operacao.csv")
    x1=[r for r in es if r['experimento']=='X1']; sched=['FCFS','SSTF','SCAN']; loads=list(OrderedDict.fromkeys(r['carga'] for r in x1))
    for met,label in [('resposta_media_ms','Resposta média (ms)'),('espera_max_ms','Espera máxima (ms)'),('deslocamento_total','Deslocamento total (cilindros)')]:
        barras('X1_'+met+'.svg','X1 — '+label,loads,sched,{(r['carga'],r['escalonador']):n(r[met]) for r in x1},label,True)
    x2=[r for r in es if r['experimento']=='X2']; g=list(OrderedDict.fromkeys(r['dispositivo']+'/'+r['carga'] for r in x2))
    barras('X2_cpu.svg','X2 — Custo de CPU conforme o modo de E/S',g,['polling','interrupcao'],{(r['dispositivo']+'/'+r['carga'],r['modo_cpu']):n(r['cpu_es_pct']) for r in x2},'% de CPU',True)
    x3=[r for r in po if r['experimento']=='X3' and r['operacao'] in ('open','read','write','create')]; ops=list(OrderedDict.fromkeys(r['operacao'] for r in x3))
    barras('X3_tempo_por_operacao.svg','X3 — Tempo médio por operação',ops,['compilador','banco_dados'],{(r['operacao'],r['carga']):n(r['tempo_medio_ms']) for r in x3},'Tempo médio (ms)')
    x4=[r for r in po if r['experimento']=='X4' and r['operacao']=='open']
    linhas('X4_open_por_profundidade.svg','X4 — Custo de open conforme a profundidade',{'Acessos por open':[(i+1,n(r['acessos_medios'])) for i,r in enumerate(x4)],'Tempo por open (ms)':[(i+1,n(r['tempo_medio_ms'])) for i,r in enumerate(x4)]},'Profundidade (diretórios)','Métrica')
    x5=next(r for r in fs if r['experimento']=='X5'); cols=['max_tabela_global','max_tabela_processo','max_soma_tabelas_processo','max_contador_aberturas']
    barras('X5_tabelas.svg','X5 — Máximos das tabelas de arquivos abertos',cols,['servidor_web'],{(c,'servidor_web'):n(x5[c]) for c in cols},'Entradas')
    x6=[r for r in es if r['experimento']=='X6' and r['cache']!='nenhuma']
    for cache in ['LRU','FIFO']:
        linhas('X6_acerto.svg' if cache=='LRU' else 'X6_acerto_fifo.svg','X6 — Taxa de acerto ('+cache+')',{'write-through':[(n(r['capacidade_cache']),n(r['acerto_cache_pct'])) for r in x6 if r['cache']==cache and r['escrita']=='write-through'],'write-back':[(n(r['capacidade_cache']),n(r['acerto_cache_pct'])) for r in x6 if r['cache']==cache and r['escrita']=='write-back']},'Capacidade (blocos)','Acertos (%)')
    lr=[r for r in x6 if r['cache']=='LRU']; linhas('X6_escrita.svg','X6 — Escritas físicas e dados perdidos (LRU write-back)',{'escritas físicas':[(n(r['capacidade_cache']),n(r['escritas_fisicas'])) for r in lr if r['escrita']=='write-back'],'perdidos na queda':[(n(r['capacidade_cache']),n(r['perdidos_na_queda'])) for r in lr if r['escrita']=='write-back']},'Capacidade (blocos)','Blocos')
    x11=[r for r in fs if r['experimento']=='X11']; alloc=[r['alocador'] for r in x11]
    custo = {('Acessos/op',r['alocador']):n(r['acessos_por_op']) for r in x11}
    custo.update({('Tempo/op (ms)',r['alocador']):n(r['tempo_medio_op_ms']) for r in x11})
    barras('X11_alocacao.svg','X11 — Custo médio dos alocadores', ['Acessos/op','Tempo/op (ms)'],alloc,custo,'Valor')
    extras=lambda r,k: next((n(z.split('=',1)[1]) for z in r['extras'].split(';') if z.startswith(k+'=')),0)
    barras('X11_fragmentacao.svg','X11 — Fragmentação e falhas', ['Segmentos livres','Falhas','Realocações'],alloc,{(c,r['alocador']):extras(r,key) for r in x11 for c,key in [('Segmentos livres','segmentos_livres'),('Falhas','falhas_alocacao'),('Realocações','realocacoes')]},'Quantidade')
    x12=[r for r in es if r['experimento']=='X12']; groups=list(OrderedDict.fromkeys(r['carga']+'/'+r['cache'] for r in x12))
    barras('X12_resposta.svg','X12 — Integração: tempo médio de resposta',groups,sched,{(r['carga']+'/'+r['cache'],r['escalonador']):n(r['resposta_media_ms']) for r in x12},'Resposta média (ms)',True)
    print('Gráficos SVG gerados em graficos/')


if __name__=='__main__': main()
