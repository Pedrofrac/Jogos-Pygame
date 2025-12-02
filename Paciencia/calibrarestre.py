import pygame
import os
from config import PASTA_ASSETS

# --- VALORES FIXOS (Tamanho da carta) ---
LARGURA = 70
ALTURA = 96
MARGIN_X = 5 # Espaço entre a carta 1 e a 2

# Começa chutando uma posição lá embaixo
POS_X = 15
POS_Y = 500 

pygame.init()

def main():
    global POS_X, POS_Y
    
    LARGURA_TELA = 1200
    ALTURA_TELA = 900
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("ACHANDO AS CARTAS EXTRAS - W/A/S/D")
    
    caminho = os.path.join(PASTA_ASSETS, "spritesheet.png")
    try:
        sheet = pygame.image.load(caminho).convert_alpha()
    except:
        print(f"ERRO: Não achei {caminho}")
        return

    largura_virtual = max(sheet.get_width(), LARGURA_TELA)
    altura_virtual = max(sheet.get_height(), ALTURA_TELA)
    camada_desenho = pygame.Surface((largura_virtual, altura_virtual))
    fonte = pygame.font.SysFont('arial', 16, bold=True)
    zoom_ativo = False

    rodando = True
    while rodando:
        camada_desenho.fill((40, 40, 40))
        camada_desenho.blit(sheet, (0, 0))
        
        # --- DESENHA OS QUADRADOS DE BUSCA ---
        # Carta Extra 1 (Vermelho)
        rect1 = pygame.Rect(POS_X, POS_Y, LARGURA, ALTURA)
        pygame.draw.rect(camada_desenho, (255, 0, 0), rect1, 2)
        
        # Carta Extra 2 (Amarelo - assume que está ao lado)
        rect2 = pygame.Rect(POS_X + LARGURA + MARGIN_X, POS_Y, LARGURA, ALTURA)
        pygame.draw.rect(camada_desenho, (255, 255, 0), rect2, 2)

        # --- ZOOM ---
        tela.fill((0,0,0))
        if zoom_ativo:
            center_x = min(max(0, POS_X - 200), largura_virtual - 400)
            center_y = min(max(0, POS_Y - 150), altura_virtual - 300)
            sub = camada_desenho.subsurface(pygame.Rect(center_x, center_y, 400, 300))
            tela.blit(pygame.transform.scale(sub, (LARGURA_TELA, ALTURA_TELA)), (0,0))
            tela.blit(fonte.render("ZOOM ATIVO (3x)", True, (0,255,0)), (20, 20))
        else:
            tela.blit(camada_desenho, (0,0))

        # --- INFO ---
        pygame.draw.rect(tela, (0,0,0), (0, 820, 1200, 80))
        info = f"EXTRA_X: {POS_X}  |  EXTRA_Y: {POS_Y}"
        tela.blit(fonte.render(info, True, (255, 215, 0)), (20, 830))
        tela.blit(fonte.render("Encaixe o quadrado VERMELHO na primeira carta extra.", True, (255, 255, 255)), (20, 855))
        tela.blit(fonte.render("Segure Z para ZOOM. SHIFT para mover rápido.", True, (0, 255, 255)), (500, 830))

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z: zoom_ativo = True
                
                step = 10 if (pygame.key.get_mods() & pygame.KMOD_SHIFT) else 1
                
                if event.key == pygame.K_d: POS_X += step
                if event.key == pygame.K_a: POS_X -= step
                if event.key == pygame.K_s: POS_Y += step
                if event.key == pygame.K_w: POS_Y -= step
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_z: zoom_ativo = False

    pygame.quit()
    print("-" * 30)
    print(f"EXTRA_X = {POS_X}")
    print(f"EXTRA_Y = {POS_Y}")
    print("-" * 30)

if __name__ == "__main__":
    main()