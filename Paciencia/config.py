import pygame

# --- CORES ---
COR_FUNDO = (34, 139, 34)
COR_BRANCA = (255, 255, 255)
COR_PRETA = (0, 0, 0)
COR_VERMELHA = (200, 0, 0)
COR_CORINGA = (148, 0, 211)
COR_AMARELA = (255, 215, 0)
COR_BOTAO = (0, 100, 0)
COR_BOTAO_HOVER = (0, 150, 0)
COR_INPUT = (20, 80, 20)
COR_CHECKBOX = (200, 200, 200)
COR_CINZA_ESCURO = (40, 40, 40)

# --- DIMENSÕES DA TELA ---
LARGURA_TELA = 1280
ALTURA_TELA = 800

# --- DIMENSÕES DA CARTA DINÂMICAS ---
# Tamanho original do recorte: 70x96
# Multiplicador de tamanho (1.6x fica bom em 1280x800)
ESCALA_CARTA = 1.6 

LARGURA_CARTA = int(70 * ESCALA_CARTA) # Aprox 112px
ALTURA_CARTA = int(96 * ESCALA_CARTA)  # Aprox 153px

ESPACO_CARTAS = 25   
OFFSET_Y_CARTA = 35  

# --- ASSETS ---
PASTA_ASSETS = "Cards (large)" 

# --- CONFIGURAÇÕES GLOBAIS ---
CONFIG = {
    "clique_duplo": False,
    "indice_verso": 0 # Começa com o primeiro fundo
}

# --- CONSTANTES ---
NAIPES = ['copas', 'ouros', 'paus', 'espadas'] 
VALORES = list(range(1, 14))