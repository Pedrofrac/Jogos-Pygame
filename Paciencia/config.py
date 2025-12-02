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

# --- DIMENSÕES ---
LARGURA_TELA = 1280
ALTURA_TELA = 800
LARGURA_CARTA = 120   
ALTURA_CARTA = 130   
ESPACO_CARTAS = 25   
OFFSET_Y_CARTA = 35  

# --- ASSETS ---
PASTA_ASSETS = "Cards (large)" 

# --- CONFIGURAÇÕES GLOBAIS ---
CONFIG = {
    "clique_duplo": False
}

# --- CONSTANTES ---
NAIPES = ['copas', 'ouros', 'paus', 'espadas'] 
VALORES = list(range(1, 14))