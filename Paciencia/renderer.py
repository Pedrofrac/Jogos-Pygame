import pygame
from config import *
from assets import *
from solitaire_rules import RegrasPaciencia

class GameRenderer:
    def __init__(self, tela):
        self.tela = tela

    def desenhar_jogo(self, jogo):
        self.tela.fill(COR_FUNDO)
        self._desenhar_cronometro(jogo.start_time)
        pygame.draw.rect(self.tela, (0, 80, 0), (0, 50, LARGURA_TELA, 160)) 
        
        self._desenhar_compra(jogo.monte_compra)
        self._desenhar_descarte(jogo.monte_descarte, jogo.visiveis_no_descarte)
        self._desenhar_fundoes(jogo.pilhas_finais)
        self._desenhar_mesa(jogo.pilhas_mesa)

        # Desenha cartas voando de volta pro monte (reciclagem)
        for c in jogo.monte_compra:
            if c.em_animacao:
                c.desenhar(self.tela)

        if jogo.carta_selecionada:
            for c in jogo.carta_selecionada: c.desenhar(self.tela)

        self._desenhar_ui_inferior(jogo)
        self._desenhar_coringa_ui(jogo.joker)

        if jogo.joker.game_over: self._desenhar_overlay("GAME OVER", COR_VERMELHA)
        elif jogo.vitoria: self._desenhar_overlay("VITORIA!", COR_AMARELA)

    def _desenhar_cronometro(self, start_time):
        segundos = (pygame.time.get_ticks() - start_time) // 1000
        txt = FONTE.render(f"Tempo: {segundos//60:02}:{segundos%60:02}", True, COR_BRANCA)
        self.tela.blit(txt, (LARGURA_TELA - 160, 10))

    def _desenhar_compra(self, monte):
        if not monte:
            pygame.draw.circle(self.tela, (0, 60, 0), (50 + LARGURA_CARTA//2, 50 + ALTURA_CARTA//2), 30, 2)
        else:
            # --- CORREÇÃO DO TOPO ESTÁTICO ---
            # Desenhamos primeiro as cartas de "fundo" (offset negativo)
            # E por último a carta do topo cravada em (50, 50)
            
            qtd = len(monte)
            # Desenha até 2 cartas de fundo para dar volume
            if qtd > 2:
                self._desenhar_verso_generico(46, 46) # Fundo 2
            if qtd > 1:
                self._desenhar_verso_generico(48, 48) # Fundo 1
            
            # Desenha o topo SEMPRE na mesma posição
            self._desenhar_verso_generico(50, 50)

    def _desenhar_verso_generico(self, x, y):
        r = pygame.Rect(x, y, LARGURA_CARTA, ALTURA_CARTA)
        if 'verso' in IMAGENS_CARTAS: 
            self.tela.blit(IMAGENS_CARTAS['verso'], r)
        else: 
            pygame.draw.rect(self.tela, (0, 0, 150), r, border_radius=5)
            pygame.draw.rect(self.tela, COR_BRANCA, r, 2, border_radius=5)

    def _desenhar_descarte(self, monte, limite_visivel):
        if not monte: return

        # Índice onde começa o leque visível
        # Se limite é 3, e temos 10 cartas, o leque começa no index 7 (10-3)
        # Cartas 0 a 6 são "soterradas"
        idx_inicio_leque = len(monte) - limite_visivel
        if idx_inicio_leque < 0: idx_inicio_leque = 0
        
        x_base = 180

        # Percorre TODAS as cartas para garantir que as soterradas não sumam
        for i, c in enumerate(monte):
            em_espera = getattr(c, 'aguardando_animacao', False)
            
            if em_espera:
                # Se está esperando sair do baralho, desenha no monte
                c.rect.topleft = (50, 50)
                c.desenhar(self.tela)
            
            elif c.em_animacao or c.arrastando:
                # Se está voando, desenha onde estiver
                c.desenhar(self.tela)
            
            else:
                # Se está parada no descarte
                if i < idx_inicio_leque:
                    # Carta soterrada/velha: Fica na base (180, 50)
                    # O game.py já virou ela pra baixo (virada=False) no update_colapso
                    c.rect.topleft = (x_base, 50)
                else:
                    # Carta do leque atual
                    offset_leque = i - idx_inicio_leque
                    c.rect.topleft = (x_base + offset_leque*25, 50)
                
                c.desenhar(self.tela)

    def _desenhar_fundoes(self, pilhas):
        simbolos = ["♥", "♦", "♣", "♠"]
        for i, pilha in enumerate(pilhas):
            rect = RegrasPaciencia.get_rect_fundacao(i)
            pygame.draw.rect(self.tela, (0, 60, 0), rect, 2, border_radius=5)
            
            t = FONTE_NAIPE_BG.render(simbolos[i], True, (0, 50, 0))
            self.tela.blit(t, t.get_rect(center=rect.center))
            
            if pilha:
                pilha[-1].desenhar(self.tela)

    def _desenhar_mesa(self, pilhas_mesa):
        for pilha in pilhas_mesa:
            for c in pilha: 
                c.desenhar(self.tela)

    def _desenhar_ui_inferior(self, jogo):
        txt_seed = FONTE_PEQUENA.render(f"Seed: {jogo.seed}", True, COR_AMARELA)
        self.tela.blit(txt_seed, (10, ALTURA_TELA - 35))
        
        btn_copy = pygame.Rect(10 + txt_seed.get_width() + 10, ALTURA_TELA - 35, 60, 20)
        pygame.draw.rect(self.tela, COR_BOTAO, btn_copy, border_radius=3)
        lbl_cpy = FONTE_PEQUENA.render("COPIAR", True, COR_BRANCA)
        self.tela.blit(lbl_cpy, (btn_copy.x + 5, btn_copy.y + 2))

        if jogo.feedback_copia:
            agora = pygame.time.get_ticks()
            if agora - jogo.feedback_timer < 2000:
                txt_ok = FONTE_PEQUENA.render("COPIADO!", True, (0, 255, 0))
                self.tela.blit(txt_ok, (btn_copy.right + 10, btn_copy.y + 2))
            else:
                jogo.feedback_copia = False

    def _desenhar_coringa_ui(self, joker):
        if not joker.habilitado or joker.game_over: return
        joker.desenhar_barra(self.tela)

    def _desenhar_overlay(self, texto, cor):
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA)); overlay.set_alpha(200)
        overlay.fill((0, 0, 0)); self.tela.blit(overlay, (0,0))
        t1 = FONTE_GRANDE.render(texto, True, cor)
        t2 = FONTE.render("Pressione R para Menu", True, COR_BRANCA)
        self.tela.blit(t1, (LARGURA_TELA//2 - t1.get_width()//2, ALTURA_TELA//2))
        self.tela.blit(t2, (LARGURA_TELA//2 - t2.get_width()//2, ALTURA_TELA//2 + 50))