import pygame
import random
import math


pygame.init()
pygame.mixer.init()

JANELA_LARGURA = 1280
JANELA_ALTURA = 720
BARRA_SCORE_ALTURA = 50
superficie_display = pygame.display.set_mode((JANELA_LARGURA, JANELA_ALTURA))
pygame.display.set_caption("A Fome do patineiro")


COR_FUNDO = (25, 120, 210)
COR_TEXTO = (255, 255, 255)
COR_BARRA = (15, 80, 160)
fonte_score = pygame.font.SysFont('tahoma', 32)


FPS = 60
clock = pygame.time.Clock()



imagem_patins_original_direita = pygame.image.load('patins_direita.png').convert_alpha()
imagem_patins_original_direita = pygame.transform.scale(imagem_patins_original_direita, (64, 64))
imagem_patins_original_esquerda = pygame.transform.flip(imagem_patins_original_direita, True, False)
imagem_pao = pygame.image.load('pao.png').convert_alpha()
som_pontuar = pygame.mixer.Sound('coin-257878.mp3')
som_especial = pygame.mixer.Sound('coin-recieved-230517.mp3')
som_pontuar.set_volume(0.3)
som_especial.set_volume(0.3)
pygame.mixer.music.load('BGM_008.WAV')
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play(-1)

game_state = "INTRO"
score = 0


velocidade_jogador = 7.0
imagem_patins_atual = imagem_patins_original_direita
retangulo_patins = imagem_patins_atual.get_rect()
direcao_jogador = "direita"


velocidade_pao = 3.0
retangulo_pao = imagem_pao.get_rect()
direcao_pao = random.choice(['CIMA', 'BAIXO', 'ESQUERDA', 'DIREITA'])
tempo_para_mudar_direcao = random.randint(2, 8) * FPS
tempo_reverso_parede = 0


def spawn_pao():
    global direcao_pao, tempo_para_mudar_direcao, tempo_reverso_parede
    distancia_minima = 250
    distancia = 0
    while distancia < distancia_minima:
        x = random.randint(0, JANELA_LARGURA - retangulo_pao.width)
        y = random.randint(BARRA_SCORE_ALTURA, JANELA_ALTURA - retangulo_pao.height)
        distancia = math.dist(retangulo_patins.center, (x + retangulo_pao.width / 2, y + retangulo_pao.height / 2))
    retangulo_pao.topleft = (x, y)
    direcao_pao = random.choice(['CIMA', 'BAIXO', 'ESQUERDA', 'DIREITA'])
    tempo_para_mudar_direcao = random.randint(2, 8) * FPS
    tempo_reverso_parede = 0

def update_hud():
    pygame.draw.rect(superficie_display, COR_BARRA, (0, 0, JANELA_LARGURA, BARRA_SCORE_ALTURA))
    texto_score = fonte_score.render(f'Score: {score}', True, COR_TEXTO)
    retangulo_texto = texto_score.get_rect(center=(JANELA_LARGURA // 2, BARRA_SCORE_ALTURA // 2))
    superficie_display.blit(texto_score, retangulo_texto)

def intro_animacao():
    global game_state
    if not hasattr(intro_animacao, 'stage2'):
        retangulo_patins.x += 6
        if retangulo_patins.left >= JANELA_LARGURA:
            intro_animacao.stage2 = True
            retangulo_patins.centerx = JANELA_LARGURA // 2
            retangulo_patins.bottom = 0
    else:
        meio_tela_y = (JANELA_ALTURA + BARRA_SCORE_ALTURA) // 2
        if retangulo_patins.centery < meio_tela_y:
            retangulo_patins.y += 6
        else:
            game_state = "JOGANDO"
            spawn_pao()

def mover_pao():
    global direcao_pao, tempo_para_mudar_direcao, tempo_reverso_parede


    if tempo_reverso_parede <= 0:
        tempo_para_mudar_direcao -= 1
        if tempo_para_mudar_direcao <= 0:
            direcao_pao = random.choice(['CIMA', 'BAIXO', 'ESQUERDA', 'DIREITA'])
            tempo_para_mudar_direcao = random.randint(2, 8) * FPS
    else:
      
        tempo_reverso_parede -= 1


    if direcao_pao == 'CIMA': retangulo_pao.y -= velocidade_pao
    elif direcao_pao == 'BAIXO': retangulo_pao.y += velocidade_pao
    elif direcao_pao == 'ESQUERDA': retangulo_pao.x -= velocidade_pao
    elif direcao_pao == 'DIREITA': retangulo_pao.x += velocidade_pao

  
    colidiu = False
    nova_direcao = None

    if retangulo_pao.top <= BARRA_SCORE_ALTURA:
        retangulo_pao.top = BARRA_SCORE_ALTURA
        nova_direcao = 'BAIXO'
        colidiu = True

    elif retangulo_pao.bottom >= JANELA_ALTURA:
        retangulo_pao.bottom = JANELA_ALTURA
        nova_direcao = 'CIMA'
        colidiu = True

    elif retangulo_pao.left <= 0:
        retangulo_pao.left = 0
        nova_direcao = 'DIREITA'
        colidiu = True

    elif retangulo_pao.right >= JANELA_LARGURA:
        retangulo_pao.right = JANELA_LARGURA
        nova_direcao = 'ESQUERDA'
        colidiu = True


    if colidiu and tempo_reverso_parede <= 0:
        direcao_pao = nova_direcao
        tempo_reverso_parede = 6 * FPS


retangulo_patins.topleft = (-retangulo_patins.width, JANELA_ALTURA // 2)
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    if game_state == "INTRO":
        intro_animacao()
    elif game_state == "JOGANDO":
        teclas = pygame.key.get_pressed()
        if (teclas[pygame.K_UP] or teclas[pygame.K_w]) and retangulo_patins.top > BARRA_SCORE_ALTURA: retangulo_patins.y -= velocidade_jogador
        if (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) and retangulo_patins.bottom < JANELA_ALTURA: retangulo_patins.y += velocidade_jogador
        if (teclas[pygame.K_LEFT] or teclas[pygame.K_a]) and retangulo_patins.left > 0:
            retangulo_patins.x -= velocidade_jogador
            direcao_jogador = "esquerda"
        if (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) and retangulo_patins.right < JANELA_LARGURA:
            retangulo_patins.x += velocidade_jogador
            direcao_jogador = "direita"

        mover_pao()

        if retangulo_patins.colliderect(retangulo_pao):
            score += 1
            if score % 10 == 0 and score != 0: som_especial.play()
            else: som_pontuar.play()
            velocidade_jogador = max(3.0, velocidade_jogador * 0.97)
            velocidade_pao *= 1.03
            spawn_pao()
    
    superficie_display.fill(COR_FUNDO)

    escala_atual = 1 + (score * 0.05)
    if direcao_jogador == 'direita':
        imagem_patins_atual = pygame.transform.scale_by(imagem_patins_original_direita, escala_atual)
    else:
        imagem_patins_atual = pygame.transform.scale_by(imagem_patins_original_esquerda, escala_atual)
    
    centro_antigo = retangulo_patins.center
    retangulo_patins = imagem_patins_atual.get_rect(center=centro_antigo)

    if game_state == "JOGANDO": superficie_display.blit(imagem_pao, retangulo_pao)
    
    superficie_display.blit(imagem_patins_atual, retangulo_patins)
    
    if game_state == "JOGANDO": update_hud()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()