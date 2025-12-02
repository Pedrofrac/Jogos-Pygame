import pygame
from config import *

class RegrasPaciencia:
    @staticmethod
    def pode_mover_para_mesa(carta_movida, carta_destino):
        if carta_movida.cor != carta_destino.cor:
            if carta_movida.valor == carta_destino.valor - 1:
                return True
        return False

    @staticmethod
    def get_rect_fundacao(index):
        base_x = LARGURA_TELA - (4 * (LARGURA_CARTA + ESPACO_CARTAS)) - 50
        return pygame.Rect(base_x + index * (LARGURA_CARTA + ESPACO_CARTAS), 50, LARGURA_CARTA, ALTURA_CARTA)

    @staticmethod
    def verificar_movimento_fundacao(carta, pilhas_finais):
        try:
            idx_alvo = NAIPES.index(carta.naipe)
            pilha_f = pilhas_finais[idx_alvo]
            if not pilha_f:
                if carta.valor == 1: return RegrasPaciencia.get_rect_fundacao(idx_alvo)
            else:
                topo = pilha_f[-1]
                if carta.valor == topo.valor + 1: return topo.rect
        except: pass
        return None