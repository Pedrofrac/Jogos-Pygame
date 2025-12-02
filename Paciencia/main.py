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
pygame.display.set_caption("Paciência - A Vingança do Coringa")
CLOCK = pygame.time.Clock()

def desenhar_botao(superficie, texto, rect, hover):
    cor = COR_BOTAO_HOVER if hover else COR_BOTAO
    pygame.draw.rect(superficie, cor, rect, border_radius=10)
    pygame.draw.rect(superficie, COR_BRANCA, rect, 2, border_radius=10)
    txt_surf = FONTE_MENU.render(texto, True, COR_BRANCA)
    txt_rect = txt_surf.get_rect(center=rect.center)
    superficie.blit(txt_surf, txt_rect)

def desenhar_checkbox(superficie, texto, rect, checked, hover):
    pygame.draw.rect(superficie, COR_CHECKBOX if hover else COR_BRANCA, rect, 2)
    if checked: pygame.draw.rect(superficie, COR_AMARELA, (rect.x+4, rect.y+4, rect.width-8, rect.height-8))
    t = FONTE.render(texto, True, COR_BRANCA)
    superficie.blit(t, (rect.right + 15, rect.y + 5))

def tela_instrucoes():
    """Exibe a tela de instruções"""
    while True:
        TELA.fill(COR_CINZA_ESCURO)
        titulo = FONTE_GRANDE.render("INSTRUÇÕES & COMANDOS", True, COR_AMARELA)
        TELA.blit(titulo, (LARGURA_TELA//2 - titulo.get_width()//2, 50))
        
        linhas = [
            "OBJETIVO: Mover todas as cartas para as 4 pilhas finais.",
            "",
            "CONTROLES:",
            "- Arrastar e Soltar: Move cartas.",
            "- Clique no Baralho: Compra cartas.",
            "- Clique Duplo: Movimento automático.",
            "- Tecla Z: Desfazer jogada.",
            "- Tecla R: Reiniciar jogo.",
            "",
            "O CORINGA (Nível Difícil):",
            "Mova uma carta antes que o tempo acabe ou Game Over!"
        ]
        
        y = 150
        for linha in linhas:
            cor = COR_AMARELA if "OBJETIVO" in linha or "CONTROLES" in linha or "CORINGA" in linha else COR_BRANCA
            fonte = FONTE_MENU if cor == COR_AMARELA else FONTE
            txt = fonte.render(linha, True, cor)
            TELA.blit(txt, (LARGURA_TELA//2 - txt.get_width()//2, y))
            y += 35

        btn_voltar = pygame.Rect(LARGURA_TELA//2 - 100, ALTURA_TELA - 100, 200, 50)
        mouse_pos = pygame.mouse.get_pos()
        desenhar_botao(TELA, "VOLTAR", btn_voltar, btn_voltar.collidepoint(mouse_pos))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: pygame.quit(); sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_voltar.collidepoint(evento.pos): return
        pygame.display.flip()

def menu_principal():
    carregar_imagens()
    largura_btn, altura_btn = 400, 60
    x_centro = LARGURA_TELA // 2 - largura_btn // 2
    
    estado_menu = 0
    seed_texto = ""
    input_box = pygame.Rect(x_centro, 150, largura_btn, 40)
    ativo_input = False
    rect_check = pygame.Rect(x_centro, 680, 30, 30)

    while True:
        TELA.fill(COR_FUNDO)
        t = FONTE_GRANDE.render("PACIÊNCIA VS CORINGA", True, COR_AMARELA)
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
        if estado_menu == 0:
            btn_facil = pygame.Rect(x_centro, start_y, largura_btn, altura_btn)
            btn_medio = pygame.Rect(x_centro, start_y + espaco, largura_btn, altura_btn)
            btn_dificil = pygame.Rect(x_centro, start_y + 2*espaco, largura_btn, altura_btn)
            
            # Botão de Tema
            btn_tema = pygame.Rect(x_centro, start_y + 3*espaco, largura_btn - 80, altura_btn)
            
            # Checkbox
            h_chk = rect_check.collidepoint(mouse_pos)
            desenhar_checkbox(TELA, "Habilitar Clique Duplo", rect_check, CONFIG["clique_duplo"], h_chk)
            if h_chk and clique: CONFIG["clique_duplo"] = not CONFIG["clique_duplo"]

            desenhar_botao(TELA, "FÁCIL (Começar)", btn_facil, btn_facil.collidepoint(mouse_pos))
            desenhar_botao(TELA, "MÉDIO (Começar)", btn_medio, btn_medio.collidepoint(mouse_pos))
            desenhar_botao(TELA, "DIFÍCIL (Seleção)", btn_dificil, btn_dificil.collidepoint(mouse_pos))
            desenhar_botao(TELA, "TEMA CARTAS", btn_tema, btn_tema.collidepoint(mouse_pos))
            
            # Miniatura da carta ao lado do botão Tema
            if 'verso' in IMAGENS_CARTAS:
                # Escala pequena para caber no menu
                mini = pygame.transform.smoothscale(IMAGENS_CARTAS['verso'], (int(LARGURA_CARTA*0.4), int(ALTURA_CARTA*0.4)))
                rect_mini = mini.get_rect(midleft=(btn_tema.right + 20, btn_tema.centery))
                TELA.blit(mini, rect_mini)
                pygame.draw.rect(TELA, COR_BRANCA, rect_mini, 2)

            # Botão de Instruções (Movido para baixo)
            btn_instr = pygame.Rect(x_centro + largura_btn + 20, start_y, 160, 60)
            # Ou podemos colocar em outro lugar, mas vou deixar o link no clique
            # para simplificar, adicionei o clique no Dificil que leva para seleção

            if clique:
                if btn_facil.collidepoint(mouse_pos): return 1, seed_texto
                if btn_medio.collidepoint(mouse_pos): return 2, seed_texto
                if btn_dificil.collidepoint(mouse_pos): estado_menu = 1
                
                # Lógica de Troca de Tema
                if btn_tema.collidepoint(mouse_pos):
                    CONFIG["indice_verso"] += 1
                    if CONFIG["indice_verso"] >= len(LISTA_VERSOS):
                        CONFIG["indice_verso"] = 0
                    atualizar_verso_atual()

        elif estado_menu == 1:
            t_sub = FONTE.render("SELECIONE O NÍVEL DO DESAFIO:", True, COR_AMARELA)
            TELA.blit(t_sub, (LARGURA_TELA//2 - t_sub.get_width()//2, 220))
            for i in range(5):
                r = pygame.Rect(x_centro, 260 + i * 70, largura_btn, 60)
                txt = f"NÍVEL {i+1}"
                if i==0: txt+=" (Normal)"
                elif i==4: txt+=" (Insano)"
                desenhar_botao(TELA, txt, r, r.collidepoint(mouse_pos))
                if r.collidepoint(mouse_pos) and clique: return 3, seed_texto
            
            r_volt = pygame.Rect(x_centro, 650, largura_btn, altura_btn)
            desenhar_botao(TELA, "VOLTAR", r_volt, r_volt.collidepoint(mouse_pos))
            if r_volt.collidepoint(mouse_pos) and clique: estado_menu = 0

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
                    jogo.gerar_relatorio("ABANDONO (Fechou)")
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    jogo.gerar_relatorio("ABANDONO (Reiniciou)")
                    rodando = False
            jogo.input(eventos)
            jogo.loop()
            renderer.desenhar_jogo(jogo)
            pygame.display.flip()

if __name__ == "__main__":
    main()