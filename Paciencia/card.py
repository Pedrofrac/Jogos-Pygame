import pygame
from config import *
from assets import IMAGENS_CARTAS, FONTE

class Carta:
    def __init__(self, valor, naipe):
        self.valor = valor
        self.naipe = naipe
        self.cor = 'vermelho' if naipe in ['copas', 'ouros'] else 'preto'
        self.virada = False
        
        # Posição Visual (Rect do Pygame usa inteiros, mas guardamos float para suavidade)
        self.rect = pygame.Rect(0, 0, LARGURA_CARTA, ALTURA_CARTA)
        self.x_float = 0.0
        self.y_float = 0.0
        
        # Lógica de Arrasto
        self.pos_original = (0, 0)
        self.arrastando = False
        self.offset_drag = (0, 0)
        
        # Sistema de Animação
        self.em_animacao = False
        self.target_x = 0
        self.target_y = 0
        self.velocidade_animacao = 0.25 # Quanto maior (0.0 a 1.0), mais rápido (Lerp factor)

    def set_pos(self, x, y):
        """Define posição instantânea (sem animação)"""
        self.rect.topleft = (x, y)
        self.x_float = float(x)
        self.y_float = float(y)
        self.target_x = float(x)
        self.target_y = float(y)
        self.em_animacao = False

    def animar_para(self, x, y, velocidade=0.2):
        """Define o destino para onde a carta deve deslizar"""
        self.target_x = float(x)
        self.target_y = float(y)
        self.velocidade_animacao = velocidade
        self.em_animacao = True

    def update(self):
        """Chamado a cada frame para calcular o movimento suave"""
        if self.arrastando:
            return # Se o mouse tá segurando, não anima automaticamente

        if self.em_animacao:
            # Fórmula de Interpolação Linear (Lerp) para suavidade
            # NovaPos = Atual + (Destino - Atual) * Velocidade
            dx = (self.target_x - self.x_float) * self.velocidade_animacao
            dy = (self.target_y - self.y_float) * self.velocidade_animacao
            
            self.x_float += dx
            self.y_float += dy
            
            # Atualiza o rect do Pygame (que precisa de inteiros)
            self.rect.x = int(self.x_float)
            self.rect.y = int(self.y_float)
            
            # Se estiver muito perto, termina a animação (snap)
            if abs(self.target_x - self.x_float) < 1 and abs(self.target_y - self.y_float) < 1:
                self.set_pos(self.target_x, self.target_y)

    def desenhar(self, superficie):
        chave = f"{self.naipe}_{self.valor}"
        if self.virada:
            if chave in IMAGENS_CARTAS:
                superficie.blit(IMAGENS_CARTAS[chave], self.rect)
            else:
                pygame.draw.rect(superficie, COR_BRANCA, self.rect, border_radius=5)
                pygame.draw.rect(superficie, COR_PRETA, self.rect, 2, border_radius=5)
                texto = FONTE.render(f"{self.valor}", True, COR_PRETA)
                superficie.blit(texto, (self.rect.x+5, self.rect.y+5))
        else:
            if 'verso' in IMAGENS_CARTAS:
                superficie.blit(IMAGENS_CARTAS['verso'], self.rect)
            else:
                pygame.draw.rect(superficie, (0, 0, 150), self.rect, border_radius=5)