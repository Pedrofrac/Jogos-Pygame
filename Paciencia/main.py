# --- main.py ---
import pygame
import sys
from config import *
from assets import *
from game import Jogo
from renderer import GameRenderer

try:
    import tkinter as tk
except ImportError:
    tk = None

TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Paciência Clássica")
CLOCK = pygame.time.Clock()

def desenhar_botao(superficie, texto, rect, hover):
    cor = COR_BOTAO_HOVER if hover else COR_BOTAO
    pygame.draw.rect(superficie, cor, rect, border_radius=10)
    pygame.draw.rect(superficie, COR_BRANCA, rect, 2, border_radius=10)
    txt_surf = FONTE_MENU.render(texto, True, COR_BRANCA)
    txt_rect = txt_surf.get_rect(center=rect.center)
    superficie.blit(txt_surf, txt_rect)

def menu_principal():
    carregar_imagens() 
    largura_btn, altura_btn = 400, 60
    x_centro = LARGURA_TELA // 2 - largura_btn // 2
    
    seed_texto = ""
    input_box = pygame.Rect(x_centro, 150, largura_btn, 40)
    ativo_input = False
    
    while True:
        TELA.fill(COR_FUNDO)
        t = FONTE_GRANDE.render("PACIÊNCIA CLÁSSICA", True, COR_AMARELA)
        TELA.blit(t, (LARGURA_TELA//2 - t.get_width()//2, 50))

        mouse_pos = pygame.mouse.get_pos(); clique = False
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: pygame.quit(); sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    clique = True
                    ativo_input = input_box.collidepoint(evento.pos)
            if evento.type == pygame.KEYDOWN:
                if ativo_input:
                    if evento.key == pygame.K_v and (evento.mod & pygame.KMOD_CTRL):
                        if tk:
                            try:
                                r = tk.Tk(); r.withdraw(); clip = r.clipboard_get(); r.destroy()
                                limpo = "".join(x for x in clip if x.isalnum()).upper()
                                seed_texto = limpo[:10]
                            except: pass
                    elif evento.key == pygame.K_BACKSPACE: seed_texto = seed_texto[:-1]
                    elif len(seed_texto) < 10 and evento.unicode.isalnum(): seed_texto += evento.unicode.upper()

        # Input Seed
        t_inst = FONTE.render("Seed (Opcional - Ctrl+V para colar):", True, COR_BRANCA)
        TELA.blit(t_inst, (input_box.x, input_box.y - 25))
        pygame.draw.rect(TELA, COR_INPUT, input_box)
        pygame.draw.rect(TELA, COR_AMARELA if ativo_input else COR_BOTAO, input_box, 2)
        t_txt = FONTE.render(seed_texto, True, COR_BRANCA)
        TELA.blit(t_txt, (input_box.x + 10, input_box.y + 10))

        start_y = 230; espaco = 75
        
        btn_facil = pygame.Rect(x_centro, start_y, largura_btn, altura_btn)
        btn_medio = pygame.Rect(x_centro, start_y + espaco, largura_btn, altura_btn)
        
        # Botão de Tema
        btn_tema = pygame.Rect(x_centro, start_y + 2*espaco, largura_btn - 80, altura_btn)
        
        desenhar_botao(TELA, "FÁCIL (1 Carta)", btn_facil, btn_facil.collidepoint(mouse_pos))
        desenhar_botao(TELA, "MÉDIO (3 Cartas)", btn_medio, btn_medio.collidepoint(mouse_pos))
        desenhar_botao(TELA, "TEMA CARTAS", btn_tema, btn_tema.collidepoint(mouse_pos))
        
        # Miniatura da carta
        if 'verso' in IMAGENS_CARTAS:
            mini = pygame.transform.smoothscale(IMAGENS_CARTAS['verso'], (int(LARGURA_CARTA*0.4), int(ALTURA_CARTA*0.4)))
            rect_mini = mini.get_rect(midleft=(btn_tema.right + 20, btn_tema.centery))
            TELA.blit(mini, rect_mini)
            pygame.draw.rect(TELA, COR_BRANCA, rect_mini, 2)

        if clique:
            if btn_facil.collidepoint(mouse_pos): return 1, seed_texto
            if btn_medio.collidepoint(mouse_pos): return 2, seed_texto
            
            if btn_tema.collidepoint(mouse_pos):
                CONFIG["indice_verso"] += 1
                atualizar_verso_atual()

        pygame.display.flip()

def main():
    renderer = GameRenderer(TELA)
    while True:
        dif, seed = menu_principal()
        jogo = Jogo(dif, seed)
        rodando = True
        while rodando:
            CLOCK.tick(144) 
            eventos = pygame.event.get()
            for ev in eventos:
                if ev.type == pygame.QUIT:
                    if jogo.vitoria:
                        jogo.gerar_relatorio("VITORIA")
                    else:
                        jogo.gerar_relatorio("ABANDONO (Fechou)")
                    pygame.quit(); sys.exit()
                
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    if jogo.vitoria:
                        jogo.gerar_relatorio("VITORIA")
                    else:
                        jogo.gerar_relatorio("ABANDONO (Reiniciou)")
                    rodando = False

            jogo.input(eventos)
            jogo.loop()
            renderer.desenhar_jogo(jogo)
            pygame.display.flip()

if __name__ == "__main__":
    main()
