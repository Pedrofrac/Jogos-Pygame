# --- joker_system.py ---
import pygame
from config import *
from assets import FONTE
from solitaire_rules import RegrasPaciencia

class SistemaCoringa:
    def __init__(self, dificuldade):
        self.dificuldade = dificuldade
        self.ativo = False
        
        # Nivel 1 (Fácil) e 2 (Médio) = SEM Coringa
        # Nível 3 (Difícil 1) = SEM Coringa (apenas difícil sem features)
        # Nível 4+ = COM Coringa
        if dificuldade <= 3:
            self.habilitado = False
        else:
            self.habilitado = True
            
        # Mapeia tempo do coringa a partir do nível 4
        tempos = {4: (10000, 8000), 5: (8000, 6000), 6: (6000, 5000), 7: (4000, 4000)}
        cfg = tempos.get(dificuldade, (10000, 8000))
        self.tempo_para_aparecer = cfg[0]
        self.tempo_de_vida = cfg[1]

        self.ultimo_movimento_time = pygame.time.get_ticks()
        self.inicio_aviso_time = 0
        self.target_rect = None
        self.game_over = False

    def reset_timer(self):
        self.ultimo_movimento_time = pygame.time.get_ticks()
        self.ativo = False

    def update(self, monte_descarte, pilhas_mesa, pilhas_finais):
        if not self.habilitado or self.game_over: return
        agora = pygame.time.get_ticks()
        
        if not self.ativo:
            if agora - self.ultimo_movimento_time > self.tempo_para_aparecer:
                rect = self._buscar_jogada_disponivel(monte_descarte, pilhas_mesa, pilhas_finais)
                if rect:
                    self.ativo = True; self.target_rect = rect; self.inicio_aviso_time = agora
                else:
                    self.ultimo_movimento_time = agora
        else:
            if agora - self.inicio_aviso_time > self.tempo_de_vida:
                self.game_over = True

    def _buscar_jogada_disponivel(self, descarte, mesa, finais):
        start_x = (LARGURA_TELA - (7 * (LARGURA_CARTA + ESPACO_CARTAS))) // 2
        if descarte:
            c = descarte[-1]
            r = RegrasPaciencia.verificar_movimento_fundacao(c, finais)
            if r: return r
            for k, p in enumerate(mesa):
                if not p and c.valor == 13: 
                    return pygame.Rect(start_x + k*(LARGURA_CARTA+ESPACO_CARTAS), 220, LARGURA_CARTA, ALTURA_CARTA)
                if p and RegrasPaciencia.pode_mover_para_mesa(c, p[-1]):
                    re = p[-1].rect.copy(); re.y += OFFSET_Y_CARTA; return re
        
        for i, pilha in enumerate(mesa):
            if not pilha: continue
            for j, c in enumerate(pilha):
                if c.virada:
                    if j == len(pilha)-1:
                         r = RegrasPaciencia.verificar_movimento_fundacao(c, finais)
                         if r: return r
                    for k, p_dest in enumerate(mesa):
                        if i == k: continue
                        if not p_dest and c.valor == 13:
                             return pygame.Rect(start_x + k*(LARGURA_CARTA+ESPACO_CARTAS), 220, LARGURA_CARTA, ALTURA_CARTA)
                        if p_dest and RegrasPaciencia.pode_mover_para_mesa(c, p_dest[-1]):
                             re = p_dest[-1].rect.copy(); re.y += OFFSET_Y_CARTA; return re
        return None
    
    def desenhar_barra(self, superficie):
        if not self.ativo: return
        agora = pygame.time.get_ticks()
        decorrido = agora - self.inicio_aviso_time
        porcentagem = 1.0 - (decorrido / self.tempo_de_vida)
        porcentagem = max(0, min(1, porcentagem))
        
        largura = 400
        h = 30
        x = LARGURA_TELA//2 - largura//2
        y = 10
        
        pygame.draw.rect(superficie, COR_PRETA, (x, y, largura, h), border_radius=5)
        cor = (255, 0, 0) if porcentagem < 0.3 else COR_CORINGA
        pygame.draw.rect(superficie, cor, (x+2, y+2, (largura-4)*porcentagem, h-4), border_radius=5)
        
        t = FONTE.render("CORINGA ESTÁ VINDO! MOVA UMA CARTA!", True, COR_BRANCA)
        superficie.blit(t, (x + largura//2 - t.get_width()//2, y + 35))
        
        if self.target_rect:
            pygame.draw.rect(superficie, cor, self.target_rect, 4)