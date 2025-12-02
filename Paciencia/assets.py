import pygame
import os
from config import *

pygame.init()

IMAGENS_CARTAS = {}
LISTA_VERSOS = [] 

# --- FONTES ---
FONTE = pygame.font.SysFont('arial', 20, bold=True)
FONTE_PEQUENA = pygame.font.SysFont('consolas', 16)
FONTE_GRANDE = pygame.font.SysFont('arial', 40, bold=True)
FONTE_MENU = pygame.font.SysFont('arial', 28, bold=True)
FONTE_NAIPE_BG = pygame.font.SysFont('segoe ui symbol', 60, bold=True) 

# --- SEUS NOVOS VALORES DE CALIBRAÇÃO ---
SRC_WIDTH = 72      
SRC_HEIGHT = 95     

MARGIN_X = 3        
MARGIN_Y = 5

START_X = 15
START_Y = 36

# Versos (Mantendo a lógica de deslocamento padrão)
# Se a frente é 15, o verso costuma ser +11 ou +12. Vamos ajustar para a coluna 8.
# 15 + 11 = 26.
START_X_VERSO = 26 
COLUNA_VERSO = 8

def limpar_cantos_arredondados(surface):
    """
    Remove uma área maior dos cantos (formato de escada) para garantir
    que não sobrem pixels azuis fora da borda arredondada.
    """
    w, h = surface.get_size()
    transparente = (0, 0, 0, 0)
    
    # Lista de offsets (dx, dy) a partir do canto para apagar.
    # Isso cria uma curva "pixelada" transparente que fica embaixo da borda preta.
    pixels_para_apagar = [
        (0,0),                         # Ponta exata
        (1,0), (2,0), (3,0),           # Borda horizontal
        (0,1), (0,2), (0,3),           # Borda vertical
        (1,1),                         # Quina interna 1
        (1,2), (2,1)                   # Quina interna 2
    ]

    try:
        for dx, dy in pixels_para_apagar:
            # Canto Superior Esquerdo
            surface.set_at((dx, dy), transparente)
            
            # Canto Superior Direito
            surface.set_at((w - 1 - dx, dy), transparente)
            
            # Canto Inferior Esquerdo
            surface.set_at((dx, h - 1 - dy), transparente)
            
            # Canto Inferior Direito
            surface.set_at((w - 1 - dx, h - 1 - dy), transparente)
    except: 
        pass

def adicionar_borda_preta(surface):
    """
    Desenha uma borda preta de 2 pixels com cantos arredondados.
    """
    w, h = surface.get_size()
    rect = pygame.Rect(0, 0, w, h)
    # border_radius=5 cria a curva. A função limpar_cantos_arredondados
    # garante que a imagem embaixo dessa curva não vaze.
    pygame.draw.rect(surface, (0, 0, 0), rect, 2, border_radius=5)

def carregar_imagens():
    global LISTA_VERSOS
    try:
        caminho = os.path.join(PASTA_ASSETS, "spritesheet.png")
        sheet = pygame.image.load(caminho).convert_alpha()
    except Exception as e:
        print(f"ERRO: Spritesheet não encontrado.")
        return

    # --- 1. CARREGAR FRENTES (NAIPES) ---
    coluna_naipes = {'espadas': 0, 'paus': 1, 'copas': 2, 'ouros': 3}

    def get_linha_index(valor):
        if valor == 13: return 0  # K
        if valor == 12: return 1  # Q
        if valor == 11: return 2  # J
        if valor == 1:  return 3  # A
        return valor + 2          # 2 a 10

    for naipe_pt in NAIPES:
        col_idx = coluna_naipes.get(naipe_pt, 0)
        for valor in VALORES:
            row_idx = get_linha_index(valor)
            
            x = START_X + (col_idx * (SRC_WIDTH + MARGIN_X))
            y = START_Y + (row_idx * (SRC_HEIGHT + MARGIN_Y))
            
            try:
                rect = pygame.Rect(x, y, SRC_WIDTH, SRC_HEIGHT)
                if x + SRC_WIDTH <= sheet.get_width():
                    img = sheet.subsurface(rect).copy()
                    
                    # 1. Limpa os cantos agressivamente
                    limpar_cantos_arredondados(img)
                    
                    # 2. Aumenta para o tamanho do jogo
                    img_final = pygame.transform.smoothscale(img, (LARGURA_CARTA, ALTURA_CARTA))
                    
                    # 3. Adiciona a borda
                    adicionar_borda_preta(img_final)
                    
                    IMAGENS_CARTAS[f"{naipe_pt}_{valor}"] = img_final
            except: pass

    # --- 2. CARREGAR VERSOS (COLUNA 8) ---
    LISTA_VERSOS = []
    
    for row in range(12):
        x = START_X_VERSO + (COLUNA_VERSO * (SRC_WIDTH + MARGIN_X))
        y = START_Y + (row * (SRC_HEIGHT + MARGIN_Y))
        
        if x + SRC_WIDTH <= sheet.get_width() and y + SRC_HEIGHT <= sheet.get_height():
            try:
                rect = pygame.Rect(x, y, SRC_WIDTH, SRC_HEIGHT)
                img = sheet.subsurface(rect).copy()
                
                centro = img.get_at((SRC_WIDTH//2, SRC_HEIGHT//2))
                if centro[3] > 0:
                    limpar_cantos_arredondados(img)
                    img_final = pygame.transform.smoothscale(img, (LARGURA_CARTA, ALTURA_CARTA))
                    adicionar_borda_preta(img_final)
                    LISTA_VERSOS.append(img_final)
            except: pass

    atualizar_verso_atual()

def atualizar_verso_atual():
    idx = CONFIG.get("indice_verso", 0)
    if LISTA_VERSOS:
        if idx >= len(LISTA_VERSOS): idx = 0
        IMAGENS_CARTAS['verso'] = LISTA_VERSOS[idx]
        CONFIG["indice_verso"] = idx
    else:
        # Fallback Azul
        s = pygame.Surface((LARGURA_CARTA, ALTURA_CARTA))
        s.fill((0, 0, 150))
        adicionar_borda_preta(s)
        IMAGENS_CARTAS['verso'] = s