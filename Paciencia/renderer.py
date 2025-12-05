# --- renderer.py ---
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
            qtd = len(monte)
            if qtd > 2: self._desenhar_verso_generico(46, 46) 
            if qtd > 1: self._desenhar_verso_generico(48, 48) 
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
        idx_inicio_leque = len(monte) - limite_visivel
        if idx_inicio_leque < 0: idx_inicio_leque = 0
        x_base = 180
        for i, c in enumerate(monte):
            em_espera = getattr(c, 'aguardando_animacao', False)
            if em_espera:
                c.rect.topleft = (50, 50)
                c.desenhar(self.tela)
            elif c.em_animacao or c.arrastando:
                c.desenhar(self.tela)
            else:
                if i < idx_inicio_leque:
                    c.rect.topleft = (x_base, 50)
                else:
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
                if len(pilha) > 1:
                    pilha[-2].desenhar(self.tela)
                pilha[-1].desenhar(self.tela)

    def _desenhar_mesa(self, pilhas_mesa):
        for pilha in pilhas_mesa:
            for c in pilha: 
                c.desenhar(self.tela)

    def _desenhar_ui_inferior(self, jogo):
        # --- LADO ESQUERDO: Comandos ---
        msg_comandos = "Z: Desfazer | R: Reiniciar"
        if CONFIG.get("clique_duplo", False):
            msg_comandos += " | Clique Duplo: ON"
            
        txt_comandos = FONTE_PEQUENA.render(msg_comandos, True, (200, 200, 200))
        self.tela.blit(txt_comandos, (20, ALTURA_TELA - 30))

        # --- LADO DIREITO: Seed e Botão Copiar ---
        btn_largura = 80
        btn_altura = 26
        margem_direita = 20
        y_pos = ALTURA_TELA - 32
        
        x_btn = LARGURA_TELA - btn_largura - margem_direita
        rect_btn = pygame.Rect(x_btn, y_pos, btn_largura, btn_altura)
        
        txt_seed = FONTE_PEQUENA.render(f"Seed: {jogo.seed}", True, COR_AMARELA)
        x_seed = x_btn - txt_seed.get_width() - 15 
        self.tela.blit(txt_seed, (x_seed, y_pos + 4))

        mouse_pos = pygame.mouse.get_pos()
        hover = rect_btn.collidepoint(mouse_pos)
        cor_bg = COR_BOTAO_HOVER if hover else COR_BOTAO
        
        pygame.draw.rect(self.tela, cor_bg, rect_btn, border_radius=5)
        pygame.draw.rect(self.tela, COR_BRANCA, rect_btn, 1, border_radius=5)
        
        lbl_cpy = FONTE_PEQUENA.render("COPIAR", True, COR_BRANCA)
        txt_rect = lbl_cpy.get_rect(center=rect_btn.center)
        self.tela.blit(lbl_cpy, txt_rect)

        if jogo.feedback_copia:
            agora = pygame.time.get_ticks()
            if agora - jogo.feedback_timer < 2000:
                txt_ok = FONTE_PEQUENA.render("COPIADO!", True, (0, 255, 0))
                self.tela.blit(txt_ok, (x_btn + 5, y_pos - 20))
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