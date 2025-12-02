import pygame
import os
from config import PASTA_ASSETS

# --- SEUS VALORES (PREENCHIDOS CORRETAMENTE AGORA) ---
LARGURA_CORTE = 71
ALTURA_CORTE = 95
MARGIN_X = 4
MARGIN_Y = 5
START_X = 15
START_Y = 36

pygame.init()

def main():
    global LARGURA_CORTE, ALTURA_CORTE, MARGIN_X, MARGIN_Y, START_X, START_Y
    
    LARGURA_TELA = 1200
    ALTURA_TELA = 900
    tela_display = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("CALIBRADOR 3.0 - SEGURE 'Z' PARA ZOOM")
    
    caminho = os.path.join(PASTA_ASSETS, "spritesheet.png")
    try:
        sheet = pygame.image.load(caminho).convert_alpha()
    except:
        print(f"ERRO: Não achei {caminho}")
        return

    # Superfície virtual onde desenhamos tudo em tamanho real (1x)
    largura_virtual = max(sheet.get_width(), LARGURA_TELA)
    altura_virtual = max(sheet.get_height(), ALTURA_TELA)
    camada_desenho = pygame.Surface((largura_virtual, altura_virtual))

    fonte = pygame.font.SysFont('arial', 16, bold=True)
    clock = pygame.time.Clock()

    zoom_ativo = False
    fator_zoom = 3.0 # 3x de Zoom

    rodando = True
    while rodando:
        # 1. Desenha tudo na camada virtual (Tamanho normal)
        camada_desenho.fill((40, 40, 40))
        camada_desenho.blit(sheet, (0, 0))
        
        # Desenha a GRADE de teste
        for col in range(4): 
            for row in range(4): 
                x = START_X + (col * (LARGURA_CORTE + MARGIN_X))
                y = START_Y + (row * (ALTURA_CORTE + MARGIN_Y))
                
                # Retângulo Vermelho (1px de espessura para precisão)
                pygame.draw.rect(camada_desenho, (255, 0, 0), (x, y, LARGURA_CORTE, ALTURA_CORTE), 1)
        
        # 2. Processa o Zoom e joga na Tela
        tela_display.fill((0,0,0))

        if zoom_ativo:
            # Foca no canto superior esquerdo
            area_visivel = pygame.Rect(0, 0, LARGURA_TELA // fator_zoom, ALTURA_TELA // fator_zoom)
            
            # Recorta a parte interessante
            sub_surface = camada_desenho.subsurface(area_visivel)
            
            # Estica (Scale)
            zoom_surface = pygame.transform.scale(sub_surface, (LARGURA_TELA, ALTURA_TELA))
            tela_display.blit(zoom_surface, (0, 0))
            
            # Aviso de Zoom
            aviso = fonte.render("!!! ZOOM ATIVO (3x) !!!", True, (0, 255, 0))
            tela_display.blit(aviso, (20, 20))
        else:
            # Sem zoom, desenha normal
            tela_display.blit(camada_desenho, (0, 0))

        # --- PAINEL DE INFORMAÇÕES (Desenhado por cima de tudo) ---
        pygame.draw.rect(tela_display, (0, 0, 0), (0, 800, 1200, 100))
        
        cor_destaque = (255, 215, 0)
        cor_texto = (255, 255, 255)

        info1 = f"INÍCIO X/Y (Use J/L/I/K): {START_X}, {START_Y}"
        info2 = f"TAMANHO W/H (Setas): {LARGURA_CORTE} x {ALTURA_CORTE}"
        info3 = f"MARGEM X/Y (W/A/S/D): {MARGIN_X}, {MARGIN_Y}"
        
        tela_display.blit(fonte.render(info1, True, cor_destaque), (20, 810))
        tela_display.blit(fonte.render(info2, True, cor_texto), (20, 840))
        tela_display.blit(fonte.render(info3, True, cor_texto), (20, 870))
        
        tela_display.blit(fonte.render("SEGURE 'Z' PARA DAR ZOOM DE 3X", True, (0, 255, 255)), (500, 810))
        tela_display.blit(fonte.render("O quadrado VERMELHO deve ser perfeito.", True, (255, 255, 255)), (500, 840))

        pygame.display.flip()
        
        # --- INPUTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            
            # Lógica do Zoom (Segurar Z)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z: zoom_ativo = True
                
                step = 10 if (pygame.key.get_mods() & pygame.KMOD_SHIFT) else 1
                
                # Posição
                if event.key == pygame.K_l: START_X += step
                if event.key == pygame.K_j: START_X -= step
                if event.key == pygame.K_k: START_Y += step
                if event.key == pygame.K_i: START_Y -= step

                # Tamanho
                if event.key == pygame.K_RIGHT: LARGURA_CORTE += 1
                if event.key == pygame.K_LEFT: LARGURA_CORTE -= 1
                if event.key == pygame.K_DOWN: ALTURA_CORTE += 1
                if event.key == pygame.K_UP: ALTURA_CORTE -= 1
                
                # Margem
                if event.key == pygame.K_d: MARGIN_X += 1
                if event.key == pygame.K_a: MARGIN_X -= 1
                if event.key == pygame.K_s: MARGIN_Y += 1
                if event.key == pygame.K_w: MARGIN_Y -= 1
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_z: zoom_ativo = False

    pygame.quit()
    print("\n" + "="*40)
    print(">>> VALORES FINAIS PARA O ASSETS.PY <<<")
    print(f"SRC_WIDTH = {LARGURA_CORTE}")
    print(f"SRC_HEIGHT = {ALTURA_CORTE}")
    print(f"MARGIN_X = {MARGIN_X}")
    print(f"MARGIN_Y = {MARGIN_Y}")
    print(f"START_X = {START_X}")
    print(f"START_Y = {START_Y}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()