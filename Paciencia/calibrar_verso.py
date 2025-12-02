import pygame
import os
from config import PASTA_ASSETS

# --- VALORES TRAVADOS (JÁ CALIBRADOS ANTES) ---
LARGURA_CARTA_IMG = 70
ALTURA_CARTA_IMG = 96
MARGIN_X = 5
MARGIN_Y = 4
START_X = 15
START_Y = 35

pygame.init()

def main():
    LARGURA_TELA = 1200
    ALTURA_TELA = 900
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("LOCALIZADOR DE VERSOS - Use as Setas")
    
    caminho = os.path.join(PASTA_ASSETS, "spritesheet.png")
    try:
        sheet = pygame.image.load(caminho).convert_alpha()
    except:
        print(f"ERRO: Não achei {caminho}")
        return

    largura_virtual = max(sheet.get_width(), LARGURA_TELA)
    altura_virtual = max(sheet.get_height(), ALTURA_TELA)
    camada_desenho = pygame.Surface((largura_virtual, altura_virtual))

    fonte = pygame.font.SysFont('arial', 20, bold=True)
    
    # Começa na coluna 9 (onde você acha que está)
    coluna_atual = 9
    linha_atual = 0
    
    zoom_ativo = False
    
    rodando = True
    while rodando:
        camada_desenho.fill((40, 40, 40))
        camada_desenho.blit(sheet, (0, 0))
        
        # Calcula onde desenhar o quadrado baseado na coluna atual
        x_box = START_X + (coluna_atual * (LARGURA_CARTA_IMG + MARGIN_X))
        y_box = START_Y + (linha_atual * (ALTURA_CARTA_IMG + MARGIN_Y))
        
        # Desenha o quadrado VERMELHO na posição atual
        pygame.draw.rect(camada_desenho, (255, 0, 0), (x_box, y_box, LARGURA_CARTA_IMG, ALTURA_CARTA_IMG), 2)
        
        # Desenha um quadrado AMARELO na próxima linha (para ver se a lista segue pra baixo)
        y_next = START_Y + ((linha_atual + 1) * (ALTURA_CARTA_IMG + MARGIN_Y))
        pygame.draw.rect(camada_desenho, (255, 255, 0), (x_box, y_next, LARGURA_CARTA_IMG, ALTURA_CARTA_IMG), 2)

        # --- ZOOM E DISPLAY ---
        tela.fill((0,0,0))
        if zoom_ativo:
            # Centraliza o zoom no quadrado vermelho
            center_x = min(max(0, x_box - 200), largura_virtual - 400)
            center_y = min(max(0, y_box - 150), altura_virtual - 300)
            area = pygame.Rect(center_x, center_y, 400, 300)
            sub = camada_desenho.subsurface(area)
            zoom = pygame.transform.scale(sub, (LARGURA_TELA, ALTURA_TELA))
            tela.blit(zoom, (0,0))
        else:
            tela.blit(camada_desenho, (0,0))

        # --- INFO ---
        pygame.draw.rect(tela, (0,0,0), (0, 800, 1200, 100))
        texto = f"COLUNA ATUAL: {coluna_atual}  |  LINHA: {linha_atual}"
        texto2 = "Use SETAS ESQUERDA/DIREITA para trocar de coluna."
        texto3 = "O quadrado VERMELHO deve estar no primeiro verso. O AMARELO no segundo."
        
        tela.blit(fonte.render(texto, True, (255, 215, 0)), (20, 810))
        tela.blit(fonte.render(texto2, True, (255, 255, 255)), (20, 840))
        tela.blit(fonte.render(texto3, True, (200, 200, 200)), (20, 870))
        tela.blit(fonte.render("Segure Z para ZOOM", True, (0, 255, 255)), (600, 810))

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z: zoom_ativo = True
                
                if event.key == pygame.K_RIGHT: coluna_atual += 1
                if event.key == pygame.K_LEFT: coluna_atual -= 1
                if event.key == pygame.K_DOWN: linha_atual += 1
                if event.key == pygame.K_UP: linha_atual -= 1
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_z: zoom_ativo = False

    pygame.quit()
    print(f"VALOR PARA COLOCAR NO ASSETS.PY -> col_verso = {coluna_atual}")

if __name__ == "__main__":
    main()