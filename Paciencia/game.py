# --- game.py ---
import pygame
import random
import string
import datetime
import copy
from config import *
from assets import *
from card import Carta
from solitaire_rules import RegrasPaciencia
from joker_system import SistemaCoringa

try:
    import tkinter as tk
except ImportError:
    tk = None

class Jogo:
    def __init__(self, dificuldade, seed_usuario=None):
        self.dificuldade = dificuldade
        self.start_time = pygame.time.get_ticks()
        self.historico = [] 
        
        # --- CONFIGURAÇÃO DE REGRAS ---
        if self.dificuldade in [1, 2]:
            CONFIG["clique_duplo"] = True
        else:
            CONFIG["clique_duplo"] = False

        self.cartas_para_virar = 1 if dificuldade == 1 else 3
        self.visiveis_no_descarte = 0
        
        if seed_usuario and seed_usuario.strip() != "":
            self.seed = seed_usuario.upper()
        else:
            chars = string.ascii_uppercase + string.digits
            self.seed = ''.join(random.choices(chars, k=6))
        
        random.seed(self.seed)
        self.baralho = self._criar_baralho()
        random.seed(None) 

        self.pilhas_mesa = [[] for _ in range(7)]
        self.pilhas_finais = [[] for _ in range(4)]
        self.monte_compra = [] 
        self.monte_descarte = [] 
        
        self.fila_animacao_inicial = [] 
        self.timer_distribuicao = 0
        
        self.fila_animacao_compra = []
        self.timer_animacao_compra = 0
        self.cartas_colapsando = [] 
        
        self._preparar_distribuicao()
        
        self.joker = SistemaCoringa(dificuldade)
        self.carta_selecionada = None 
        self.origem_selecao = None 
        self.index_origem = None 
        self.ultimo_clique_time = 0
        self.ultima_carta_clicada = None
        self.feedback_copia = False
        self.feedback_timer = 0
        self.vitoria = False
        self.relatorio_gerado = False

    def salvar_estado(self):
        # deepcopy salva exatamente a posição (x,y) daquele momento
        estado = {
            'mesa': copy.deepcopy(self.pilhas_mesa),
            'finais': copy.deepcopy(self.pilhas_finais),
            'compra': copy.deepcopy(self.monte_compra),
            'descarte': copy.deepcopy(self.monte_descarte),
            'visiveis': self.visiveis_no_descarte,
            'score': 0 
        }
        self.historico.append(estado)
        if len(self.historico) > 50:
            self.historico.pop(0)

    def desfazer(self):
        if not self.historico:
            return

        # 1. MAPEAMENTO VISUAL: Guardar onde as cartas estão AGORA na tela.
        # Isso impede o "teletransporte" ou o "pulo" lateral.
        posicoes_visuais = {}
        todas_listas_atuais = [self.monte_compra, self.monte_descarte] + self.pilhas_mesa + self.pilhas_finais
        for lista in todas_listas_atuais:
            for c in lista:
                chave = f"{c.naipe}_{c.valor}"
                posicoes_visuais[chave] = (c.x_float, c.y_float)

        # 2. RESTAURAÇÃO DO ESTADO (Lógica)
        estado = self.historico.pop()
        
        self.pilhas_mesa = estado['mesa']
        self.pilhas_finais = estado['finais']
        self.monte_compra = estado['compra']
        self.monte_descarte = estado['descarte']
        self.visiveis_no_descarte = estado['visiveis']
        
        # 3. SINCRONIA E RE-ANIMAÇÃO
        # Aplicamos a posição visual antiga nas cartas restauradas
        todas_listas_restauradas = [self.monte_compra, self.monte_descarte] + self.pilhas_mesa + self.pilhas_finais
        
        for lista in todas_listas_restauradas:
            for c in lista:
                chave = f"{c.naipe}_{c.valor}"
                if chave in posicoes_visuais:
                    # A carta restaurada assume a posição visual da carta que estava na tela
                    x_antigo, y_antigo = posicoes_visuais[chave]
                    c.set_pos(x_antigo, y_antigo)
                
                # Reseta estados de arrasto para evitar bugs
                c.arrastando = False
                c.em_animacao = False
        
        # 4. FORÇAR ALINHAMENTO (Animação suave de volta para o lugar correto)
        self.update_posicoes_mesa() # Arruma a mesa
        self._alinhar_finais()      # Arruma as fundações
        self._alinhar_descarte()    # Arruma o descarte
        self._alinhar_compra()      # Arruma o monte de compra

        # Limpa filas de animação pendentes
        self.fila_animacao_compra = []
        self.cartas_colapsando = []
        self.carta_selecionada = None
        
        self.joker.reset_timer()

    # --- NOVOS MÉTODOS DE ALINHAMENTO PARA O UNDO ---
    def _alinhar_finais(self):
        """Garante que as cartas nas fundações voltem para o lugar certo suavemente"""
        for i, pilha in enumerate(self.pilhas_finais):
            rect = RegrasPaciencia.get_rect_fundacao(i)
            for c in pilha:
                c.animar_para(rect.x, rect.y, velocidade=0.2)

    def _alinhar_descarte(self):
        """Recalcula o leque do descarte e anima"""
        if not self.monte_descarte: return
        total = len(self.monte_descarte)
        # Recalcula quantas mostrar baseado no estado restaurado
        visiveis = self.visiveis_no_descarte
        inicio_leque = max(0, total - visiveis)
        x_base = 180
        
        for i, c in enumerate(self.monte_descarte):
            if i < inicio_leque:
                # Escondidas sob o monte
                c.animar_para(x_base, 50, velocidade=0.2)
            else:
                # No leque visível
                offset = i - inicio_leque
                c.animar_para(x_base + (offset * 25), 50, velocidade=0.2)

    def _alinhar_compra(self):
        """Manda o monte de compra para a posição inicial"""
        for c in self.monte_compra:
            c.animar_para(50, 50, velocidade=0.2)
    # -----------------------------------------------------

    def _criar_baralho(self):
        cartas = [Carta(v, n) for n in NAIPES for v in VALORES]
        random.shuffle(cartas)
        for c in cartas:
            c.set_pos(50, 50) 
            c.virada = False 
        return cartas

    def _preparar_distribuicao(self):
        start_x = (LARGURA_TELA - (7 * (LARGURA_CARTA + ESPACO_CARTAS))) // 2
        cartas_temp = self.baralho[:]
        self.baralho = []
        
        indice_carta = 0
        for i in range(7):
            for j in range(i + 1):
                c = cartas_temp[indice_carta]
                indice_carta += 1
                dest_x = start_x + i * (LARGURA_CARTA + ESPACO_CARTAS)
                dest_y = 220 + j * OFFSET_Y_CARTA
                should_flip = (j == i)
                self.pilhas_mesa[i].append(c)
                self.fila_animacao_inicial.append((c, dest_x, dest_y, should_flip))
        
        self.monte_compra = cartas_temp[indice_carta:]

    def update_animacao_inicial(self):
        if not self.fila_animacao_inicial: return
        agora = pygame.time.get_ticks()
        if agora - self.timer_distribuicao > 30:
            c, dx, dy, virar = self.fila_animacao_inicial.pop(0)
            c.animar_para(dx, dy, velocidade=0.15)
            if virar: c.virada = True
            self.timer_distribuicao = agora

    def update_animacao_compra(self):
        if not self.fila_animacao_compra: return
        agora = pygame.time.get_ticks()
        if agora - self.timer_animacao_compra > 80:
            c, dest_x, dest_y = self.fila_animacao_compra.pop(0)
            c.aguardando_animacao = False
            c.virada = True 
            c.animar_para(dest_x, dest_y, velocidade=0.06)
            self.timer_animacao_compra = agora

    def update_colapso(self):
        for i in range(len(self.cartas_colapsando) - 1, -1, -1):
            c = self.cartas_colapsando[i]
            if not c.em_animacao:
                self.cartas_colapsando.pop(i)

    def update_cartas(self):
        all_lists = [self.monte_compra, self.monte_descarte] + self.pilhas_mesa + self.pilhas_finais
        for lista in all_lists:
            for c in lista:
                c.update()
        if self.carta_selecionada:
            for c in self.carta_selecionada: c.update()

    def update_posicoes_mesa(self):
        start_x = (LARGURA_TELA - (7 * (LARGURA_CARTA + ESPACO_CARTAS))) // 2
        for i, pilha in enumerate(self.pilhas_mesa):
            x = start_x + i * (LARGURA_CARTA + ESPACO_CARTAS)
            for j, c in enumerate(pilha):
                if not c.arrastando:
                    c.animar_para(x, 220 + j * OFFSET_Y_CARTA, velocidade=0.2)
                    # Atualiza pos_original para o próximo drag ser correto
                    c.pos_original = (x, 220 + j * OFFSET_Y_CARTA)

    def tentar_movimento_automatico(self, carta):
        rect_f = RegrasPaciencia.verificar_movimento_fundacao(carta, self.pilhas_finais)
        eh_topo = False
        
        if carta in self.monte_descarte:
            if self.visiveis_no_descarte > 0 and carta == self.monte_descarte[-1]:
                eh_topo = True
        else:
            for p in self.pilhas_mesa:
                if p and p[-1] == carta: eh_topo = True; break
            for p in self.pilhas_finais:
                if p and p[-1] == carta: eh_topo = True; break

        if eh_topo and rect_f:
            self.salvar_estado()
            idx = NAIPES.index(carta.naipe)
            self.pilhas_finais[idx].append(carta)
            self._remover_da_origem_obj(carta)
            carta.animar_para(rect_f.x, rect_f.y, velocidade=0.2)
            self.joker.reset_timer()
            return True
        
        grupo_cartas = [carta]
        origem_mesa = False
        
        if carta not in self.monte_descarte and not any(carta in p for p in self.pilhas_finais):
            for p in self.pilhas_mesa:
                if carta in p:
                    idx_c = p.index(carta)
                    grupo_cartas = p[idx_c:]
                    origem_mesa = True
                    break
        
        cabeça = grupo_cartas[0]
        start_x = (LARGURA_TELA - (7 * (LARGURA_CARTA + ESPACO_CARTAS))) // 2
        
        for k, pilha_destino in enumerate(self.pilhas_mesa):
            if origem_mesa and pilha_destino and cabeça in pilha_destino: continue
            
            moveu = False
            dest_x, dest_y = 0, 0
            
            if not pilha_destino:
                if cabeça.valor == 13: 
                    dest_x = start_x + k*(LARGURA_CARTA+ESPACO_CARTAS)
                    dest_y = 220
                    moveu = True
            else:
                topo = pilha_destino[-1]
                if RegrasPaciencia.pode_mover_para_mesa(cabeça, topo):
                    dest_x = topo.rect.x
                    dest_y = topo.rect.y + OFFSET_Y_CARTA
                    moveu = True
            
            if moveu:
                self.salvar_estado()
                self._remover_grupo_da_origem(grupo_cartas)
                for i, c in enumerate(grupo_cartas):
                    c.arrastando = False
                    c.animar_para(dest_x, dest_y + (i * OFFSET_Y_CARTA), velocidade=0.2)
                    pilha_destino.append(c)
                self.joker.reset_timer()
                return True
        return False

    def _remover_da_origem_obj(self, carta):
        if carta in self.monte_descarte: 
            self.monte_descarte.remove(carta)
            
            if self.visiveis_no_descarte > 1:
                self.visiveis_no_descarte -= 1
            else:
                if len(self.monte_descarte) > 0:
                    self.visiveis_no_descarte = min(len(self.monte_descarte), 3)
                else:
                    self.visiveis_no_descarte = 0
            return 

        for p in self.pilhas_mesa:
            if carta in p:
                p.remove(carta)
                if p and not p[-1].virada: p[-1].virada = True
                return 

        for p in self.pilhas_finais:
            if carta in p:
                p.remove(carta)
                return

    def _remover_grupo_da_origem(self, lista_cartas):
        c = lista_cartas[0]
        for p in self.pilhas_finais:
            if c in p:
                p.remove(c)
                return

        if c in self.monte_descarte:
            self.monte_descarte.remove(c)
            if self.visiveis_no_descarte > 1:
                self.visiveis_no_descarte -= 1
            else:
                if len(self.monte_descarte) > 0:
                    self.visiveis_no_descarte = min(len(self.monte_descarte), 3)
                else:
                    self.visiveis_no_descarte = 0
        else:
            for p in self.pilhas_mesa:
                if c in p:
                    idx = p.index(c)
                    del p[idx:]
                    if p and not p[-1].virada: p[-1].virada = True
                    return

    def gerar_relatorio(self, resultado):
        if self.relatorio_gerado: return
        try:
            with open("relatorio_partidas.txt", "a") as f:
                d = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                f.write(f"Data: {d} | Seed: {self.seed} | Nivel: {self.dificuldade} | Res: {resultado}\n")
        except: pass
        self.relatorio_gerado = True

    def copiar_seed(self):
        self.feedback_copia = True
        self.feedback_timer = pygame.time.get_ticks()
        if tk:
            try:
                r = tk.Tk(); r.withdraw(); r.clipboard_clear(); r.clipboard_append(self.seed); r.update(); r.destroy()
            except: pass

    def input(self, eventos):
        if self.joker.game_over or self.vitoria: return

        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    pos = evento.pos
                    agora = pygame.time.get_ticks()

                    btn_copiar_rect = pygame.Rect(LARGURA_TELA - 100, ALTURA_TELA - 32, 80, 26)
                    if btn_copiar_rect.collidepoint(pos):
                        self.copiar_seed(); return

                    if pygame.Rect(50, 50, LARGURA_CARTA, ALTURA_CARTA).collidepoint(pos):
                        if self.fila_animacao_compra: 
                            return

                        self.salvar_estado() 
                        self.joker.reset_timer()
                        
                        if self.monte_compra:
                            cartas_visiveis_agora = []
                            if self.visiveis_no_descarte > 0 and self.monte_descarte:
                                cartas_visiveis_agora = self.monte_descarte[-self.visiveis_no_descarte:]

                            qtd_compra = min(self.cartas_para_virar, len(self.monte_compra))
                            novas_cartas = []
                            for _ in range(qtd_compra):
                                c = self.monte_compra.pop()
                                self.monte_descarte.append(c)
                                novas_cartas.append(c)

                            total_no_descarte = len(self.monte_descarte)
                            self.visiveis_no_descarte = min(total_no_descarte, 3)
                            cartas_visiveis_futuro = self.monte_descarte[-self.visiveis_no_descarte:]
                            
                            for c in cartas_visiveis_agora:
                                if c in cartas_visiveis_futuro:
                                    idx_novo = cartas_visiveis_futuro.index(c)
                                    dest_x = 180 + (idx_novo * 25)
                                    c.animar_para(dest_x, 50, velocidade=0.1)
                                else:
                                    c.animar_para(180, 50, velocidade=0.1)

                            self.fila_animacao_compra = [] 
                            self.timer_animacao_compra = agora + 50 
                            
                            for c in novas_cartas:
                                c.set_pos(50, 50) 
                                c.virada = False 
                                c.aguardando_animacao = True
                                
                                idx_novo = cartas_visiveis_futuro.index(c)
                                dest_x = 180 + (idx_novo * 25)
                                self.fila_animacao_compra.append((c, dest_x, 50))

                        else:
                            self.monte_compra = self.monte_descarte[::-1]
                            self.monte_descarte = []
                            self.visiveis_no_descarte = 0 
                            
                            for c in self.monte_compra: 
                                c.virada = False 
                                c.aguardando_animacao = False 
                                c.animar_para(50, 50, velocidade=0.2) 
                        return

                    carta_clicada = None; origem = None; idx = None
                    
                    if self.monte_descarte and self.visiveis_no_descarte > 0:
                        topo = self.monte_descarte[-1]
                        if topo.rect.collidepoint(pos): carta_clicada = topo; origem = 'descarte'
                    
                    if not carta_clicada:
                        for i, p in enumerate(self.pilhas_mesa):
                            for j in range(len(p)-1, -1, -1):
                                if p[j].virada and p[j].rect.collidepoint(pos):
                                    carta_clicada = p[j]; origem = 'mesa'; idx = i; break
                            if carta_clicada: break
                    
                    if not carta_clicada:
                         for i, p in enumerate(self.pilhas_finais):
                            if p and p[-1].rect.collidepoint(pos):
                                carta_clicada = p[-1]; origem = 'fundacao'; idx = i; break

                    if carta_clicada:
                        if CONFIG["clique_duplo"]:
                            if self.ultima_carta_clicada == carta_clicada and agora - self.ultimo_clique_time < 500:
                                if self.tentar_movimento_automatico(carta_clicada):
                                    self.ultima_carta_clicada = None; self.update_posicoes_mesa(); return

                        self.ultima_carta_clicada = carta_clicada; self.ultimo_clique_time = agora
                        self.joker.reset_timer()
                        
                        if origem == 'mesa':
                            ic = self.pilhas_mesa[idx].index(carta_clicada)
                            self.carta_selecionada = self.pilhas_mesa[idx][ic:]
                        else: self.carta_selecionada = [carta_clicada]
                        
                        self.origem_selecao = origem; self.index_origem = idx
                        for c in self.carta_selecionada:
                            c.em_animacao = False 
                            c.pos_original = c.rect.topleft; c.arrastando = True
                            c.offset_drag = (c.rect.x-pos[0], c.rect.y-pos[1])

            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1 and self.carta_selecionada:
                    self._processar_drop()
                    self.carta_selecionada = None
                    self.update_posicoes_mesa()

            elif evento.type == pygame.MOUSEMOTION and self.carta_selecionada:
                pos = evento.pos
                lider = self.carta_selecionada[0]
                lider.set_pos(pos[0] + lider.offset_drag[0], pos[1] + lider.offset_drag[1])
                for k in range(1, len(self.carta_selecionada)):
                    s = self.carta_selecionada[k]
                    s.set_pos(lider.rect.x, lider.rect.y + (k * OFFSET_Y_CARTA))

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_z:
                    self.desfazer()

    def _processar_drop(self):
        cabeça = self.carta_selecionada[0]
        moveu = False
        
        if len(self.carta_selecionada) == 1:
            for i in range(4):
                if cabeça.rect.colliderect(RegrasPaciencia.get_rect_fundacao(i)):
                    if cabeça.naipe == NAIPES[i]:
                        pilha = self.pilhas_finais[i]
                        ok = False
                        if not pilha and cabeça.valor == 1: ok = True
                        elif pilha and cabeça.valor == pilha[-1].valor + 1 and pilha[-1] != cabeça: ok = True
                        if ok:
                            self.salvar_estado() 
                            self._remover_grupo_da_origem(self.carta_selecionada)
                            cabeça.arrastando = False
                            dest = RegrasPaciencia.get_rect_fundacao(i)
                            cabeça.animar_para(dest.x, dest.y, velocidade=0.2) 
                            pilha.append(cabeça); moveu = True
                    break
        
        start_x = (LARGURA_TELA - (7 * (LARGURA_CARTA + ESPACO_CARTAS))) // 2
        if not moveu:
            for i in range(7):
                area = pygame.Rect(start_x + i*(LARGURA_CARTA+ESPACO_CARTAS), 220, LARGURA_CARTA, ALTURA_CARTA)
                pilha_dest = self.pilhas_mesa[i]
                if self.origem_selecao == 'mesa' and self.index_origem == i: continue

                aceita = False
                dest_x, dest_y = 0, 0
                if not pilha_dest:
                    if cabeça.rect.colliderect(area) and cabeça.valor == 13: 
                        aceita = True
                        dest_x, dest_y = area.x, area.y
                else:
                    topo = pilha_dest[-1]
                    if topo != cabeça and cabeça.rect.colliderect(topo.rect):
                        if RegrasPaciencia.pode_mover_para_mesa(cabeça, topo): 
                            aceita = True
                            dest_x, dest_y = topo.rect.x, topo.rect.y + OFFSET_Y_CARTA
                if aceita:
                    self.salvar_estado() 
                    self._remover_grupo_da_origem(self.carta_selecionada)
                    for k, c in enumerate(self.carta_selecionada): 
                        c.arrastando=False
                        c.animar_para(dest_x, dest_y + (k * OFFSET_Y_CARTA), velocidade=0.2)
                        pilha_dest.append(c)
                    moveu = True; break
        
        if not moveu:
             for c in self.carta_selecionada: 
                 c.arrastando = False
                 c.animar_para(c.pos_original[0], c.pos_original[1], velocidade=0.2)

    def loop(self):
        self.update_animacao_inicial()
        self.update_animacao_compra()
        self.update_colapso()
        self.update_cartas()
        self.joker.update(self.monte_descarte, self.pilhas_mesa, self.pilhas_finais)
        if sum(len(p) for p in self.pilhas_finais) == 52:
            self.vitoria = True