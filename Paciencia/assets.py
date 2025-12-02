import pygame
import os
from config import *

pygame.init()

IMAGENS_CARTAS = {}
FONTE = pygame.font.SysFont('arial', 20, bold=True)
FONTE_PEQUENA = pygame.font.SysFont('consolas', 16)
FONTE_GRANDE = pygame.font.SysFont('arial', 40, bold=True)
FONTE_MENU = pygame.font.SysFont('arial', 28, bold=True)
FONTE_NAIPE_BG = pygame.font.SysFont('segoe ui symbol', 60, bold=True) 

def carregar_imagens():
    mapa_naipes = {'copas': 'hearts', 'ouros': 'diamonds', 'paus': 'clubs', 'espadas': 'spades'}
    try:
        caminho = os.path.join(PASTA_ASSETS, "card_back.png")
        img = pygame.image.load(caminho).convert_alpha()
        IMAGENS_CARTAS['verso'] = pygame.transform.scale(img, (LARGURA_CARTA, ALTURA_CARTA))
    except: pass

    for naipe_pt in NAIPES:
        naipe_en = mapa_naipes[naipe_pt]
        for valor in VALORES:
            if valor == 1: v_str = "A"
            elif valor == 11: v_str = "J"
            elif valor == 12: v_str = "Q"
            elif valor == 13: v_str = "K"
            else: v_str = f"{valor:02d}"
            
            nome_arquivo = f"card_{naipe_en}_{v_str}.png"
            caminho_completo = os.path.join(PASTA_ASSETS, nome_arquivo)
            try:
                img = pygame.image.load(caminho_completo).convert_alpha()
                img = pygame.transform.scale(img, (LARGURA_CARTA, ALTURA_CARTA))
                IMAGENS_CARTAS[f"{naipe_pt}_{valor}"] = img
            except: pass