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

# --- CONFIGURAÇÃO DE RECORTE ---
SRC_WIDTH = 72      
SRC_HEIGHT = 95     

MARGIN_X = 3        
MARGIN_Y = 5

START_X = 15
START_Y = 36

# --- CONFIGURAÇÃO DOS VERSOS ---
START_X_VERSO_PADRAO = 26 
COLUNA_VERSO_PADRAO = 8 

# Bloco Extra
START_X_EXTRA = 17
START_Y_EXTRA = 1369

def limpar_cantos_arredondados(surface):
    w, h = surface.get_size()
    transparente = (0, 0, 0, 0)
    pixels_para_apagar = [
        (0,0), (1,0), (2,0), (3,0),
        (0,1), (0,2), (0,3),
        (1,1), (1,2), (2,1)
    ]
    try:
        for dx, dy in pixels_para_apagar:
            surface.set_at((dx, dy), transparente)
            surface.set_at((w - 1 - dx, dy), transparente)
            surface.set_at((dx, h - 1 - dy), transparente)
            surface.set_at((w - 1 - dx, h - 1 - dy), transparente)
    except: pass

def adicionar_borda_preta(surface):
    w, h = surface.get_size()
    pygame.draw.rect(surface, (0, 0, 0), (0, 0, w, h), 2, border_radius=5)

def carregar_imagens():
    global LISTA_VERSOS
    try:
        caminho = os.path.join(PASTA_ASSETS, "spritesheet.png")
        sheet = pygame.image.load(caminho).convert_alpha()
    except Exception as e:
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
                if x + SRC_WIDTH <= sheet.get_width() and y + SRC_HEIGHT <= sheet.get_height():
                    rect = pygame.Rect(x, y, SRC_WIDTH, SRC_HEIGHT)
                    img = sheet.subsurface(rect).copy()
                    limpar_cantos_arredondados(img)
                    img_final = pygame.transform.smoothscale(img, (LARGURA_CARTA, ALTURA_CARTA))
                    adicionar_borda_preta(img_final)
                    IMAGENS_CARTAS[f"{naipe_pt}_{valor}"] = img_final
            except: pass

    # --- 2. CARREGAR VERSOS ---
    LISTA_VERSOS = []
    
    versos_prioritarios = [] 
    versos_padrao = []       

    # PARTE A: Versos Extras (Antigos 14 e 13) - MANTIDO
    row_ex = 0 
    cols_ordem = [1, 0] 

    for col_ex in cols_ordem:
        x = START_X_EXTRA + (col_ex * (SRC_WIDTH + MARGIN_X))
        y = START_Y_EXTRA + (row_ex * (SRC_HEIGHT + MARGIN_Y))
        
        if x + SRC_WIDTH <= sheet.get_width() and y + SRC_HEIGHT <= sheet.get_height():
            try:
                rect = pygame.Rect(x, y, SRC_WIDTH, SRC_HEIGHT)
                img = sheet.subsurface(rect).copy()
                centro = img.get_at((SRC_WIDTH//2, SRC_HEIGHT//2))
                
                if centro[3] > 0:
                    limpar_cantos_arredondados(img)
                    img_final = pygame.transform.smoothscale(img, (LARGURA_CARTA, ALTURA_CARTA))
                    adicionar_borda_preta(img_final)
                    versos_prioritarios.append(img_final)
            except: pass

    # PARTE B: Versos da Coluna Padrão
    # ALTERADO: De range(12) para range(10) para remover os 2 últimos
    for row in range(10): 
        x = START_X_VERSO_PADRAO + (COLUNA_VERSO_PADRAO * (SRC_WIDTH + MARGIN_X))
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
                    versos_padrao.append(img_final)
            except: pass

    # Monta a lista final: 14 -> 13 -> 1 ao 10
    LISTA_VERSOS = versos_prioritarios + versos_padrao
    
    atualizar_verso_atual()

def atualizar_verso_atual():
    idx = CONFIG.get("indice_verso", 0)
    if LISTA_VERSOS:
        if idx >= len(LISTA_VERSOS): 
            idx = 0
            CONFIG["indice_verso"] = 0
        IMAGENS_CARTAS['verso'] = LISTA_VERSOS[idx]
    else:
        s = pygame.Surface((LARGURA_CARTA, ALTURA_CARTA))
        s.fill((0, 0, 150))
        adicionar_borda_preta(s)
        IMAGENS_CARTAS['verso'] = s