import pygame
import sys

# Inicialização do Pygame
pygame.init()

# Configurações da Tela
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Torre de Hanói")

# Cores
BRANCO = (255, 255, 255)
AZUL_ESCURO = (44, 62, 80)
AZUL_CLARO = (52, 152, 219)
CINZA = (189, 195, 199)
VERMELHO = (231, 76, 60)
VERDE = (46, 204, 113)
AMARELO = (241, 196, 15)
LARANJA = (230, 126, 34)
ROXO = (155, 89, 182)

# Dicionário para mapear o tamanho do disco à sua cor
CORES_DISCOS = {1: VERMELHO, 2: VERDE, 3: AMARELO, 4: LARANJA, 5: ROXO}

# Fontes
fonte = pygame.font.SysFont(None, 36)
fonte_grande = pygame.font.SysFont(None, 96)
fonte_titulo = pygame.font.SysFont(None, 80)

# Tela atual: "menu", "regras" ou "jogo"
estado = "menu"

# Quantidade de discos escolhida no menu (entre 3 e 5)
MIN_DISCOS, MAX_DISCOS = 3, 5
num_discos = 3

# Estado Inicial do Jogo
movimentos = 0
tempo_inicial = pygame.time.get_ticks()
venceu = False
tempo_final = 0

# As listas operam como "Pilhas". O último item (à direita) é o topo da torre.
# O maior número é o maior disco, 1 é o menor.
torres = {
    "A": [],
    "B": [],
    "C": []
}

# Posições Centrais de cada pino no eixo X (Para alinhar os discos)
CENTROS_X = {"A": 210, "B": 410, "C": 610}
CHAO_Y = 500
ALTURA_DISCO = 25

def largura_disco(tamanho):
    """Largura visual do disco (o maior disco cabe dentro do espaçamento dos pinos)."""
    return tamanho * 28 + 36

# Variáveis do Drag and Drop
disco_arrastado = None    # Guarda o número (tamanho) do disco
pino_origem = None        # Lembra de onde o disco saiu
rect_arrastado = None     # O "Retângulo" visual que segue o mouse
offset_x, offset_y = 0, 0 # Para o mouse segurar o disco no ponto exato do clique

# Botões
BOTAO_REINICIAR = pygame.Rect(LARGURA // 2 - 80, 540, 160, 40)
BOTAO_MENU = pygame.Rect(LARGURA // 2 - 80 - 180, 540, 160, 40)
BOTAO_INICIAR = pygame.Rect(LARGURA // 2 - 110, 280, 220, 50)
BOTAO_REGRAS = pygame.Rect(LARGURA // 2 - 110, 350, 220, 50)
BOTAO_VOLTAR = pygame.Rect(LARGURA // 2 - 80, 520, 160, 40)
BOTAO_MENOS = pygame.Rect(LARGURA // 2 - 130, 470, 50, 50)
BOTAO_MAIS = pygame.Rect(LARGURA // 2 + 80, 470, 50, 50)

REGRAS = [
    "Objetivo: mover todos os discos do pino A para o pino C.",
    "",
    "1. Mova apenas um disco por vez.",
    "2. Só é possível pegar o disco que está no topo de um pino.",
    "3. Nunca coloque um disco maior sobre um disco menor.",
    "4. Arraste os discos com o mouse (botão esquerdo).",
    "",
    "Com N discos, o mínimo de movimentos é 2^N - 1.",
    "Atalho: tecla R reinicia a partida.",
]

def iniciar_partida():
    """Prepara uma nova partida com a quantidade de discos escolhida."""
    global movimentos, tempo_inicial, venceu, tempo_final
    global disco_arrastado, pino_origem, rect_arrastado
    movimentos = 0
    tempo_inicial = pygame.time.get_ticks()
    venceu = False
    tempo_final = 0
    torres["A"] = list(range(num_discos, 0, -1))
    torres["B"] = []
    torres["C"] = []
    disco_arrastado = None
    pino_origem = None
    rect_arrastado = None

def reiniciar():
    """Volta o jogo ao estado inicial."""
    iniciar_partida()

def desenhar_botao(rect, texto, cor=AZUL_ESCURO):
    """Desenha um botão com destaque ao passar o mouse."""
    cor_atual = AZUL_CLARO if rect.collidepoint(mouse_x, mouse_y) else cor
    pygame.draw.rect(tela, cor_atual, rect, border_radius=8)
    surf = fonte.render(texto, True, BRANCO)
    tela.blit(surf, surf.get_rect(center=rect.center))

clock = pygame.time.Clock()

while True:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # --- MENU INICIAL ---
        elif estado == "menu":
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if BOTAO_INICIAR.collidepoint(evento.pos):
                    iniciar_partida()
                    estado = "jogo"
                elif BOTAO_REGRAS.collidepoint(evento.pos):
                    estado = "regras"
                elif BOTAO_MENOS.collidepoint(evento.pos):
                    num_discos = max(MIN_DISCOS, num_discos - 1)
                elif BOTAO_MAIS.collidepoint(evento.pos):
                    num_discos = min(MAX_DISCOS, num_discos + 1)

        # --- TELA DE REGRAS ---
        elif estado == "regras":
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if BOTAO_VOLTAR.collidepoint(evento.pos):
                    estado = "menu"
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                estado = "menu"

        # --- JOGO ---
        # 0. REINICIAR (tecla R)
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            reiniciar()

        # 1. CLICOU PARA PEGAR UM DISCO
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1 and BOTAO_REINICIAR.collidepoint(evento.pos):
                reiniciar()
            elif evento.button == 1 and BOTAO_MENU.collidepoint(evento.pos):
                estado = "menu"
            elif evento.button == 1 and not venceu:  # Botão esquerdo do mouse
                # Procurar se clicou no disco do topo de alguma torre
                for pino, discos in torres.items():
                    if len(discos) > 0:
                        tamanho = discos[-1] # Pega o disco do topo
                        largura = largura_disco(tamanho)
                        
                        # Calcula onde esse disco está desenhado
                        x_rect = CENTROS_X[pino] - (largura // 2)
                        y_rect = CHAO_Y - (len(discos) * ALTURA_DISCO)
                        
                        rect_disco = pygame.Rect(x_rect, y_rect, largura, ALTURA_DISCO)
                        
                        # Verifica se o mouse clicou dentro deste disco
                        if rect_disco.collidepoint(mouse_x, mouse_y):
                            disco_arrastado = torres[pino].pop() # Remove o disco do pino
                            pino_origem = pino
                            rect_arrastado = rect_disco
                            
                            # Calcula a diferença entre o clique e o canto do disco
                            offset_x = rect_disco.x - mouse_x
                            offset_y = rect_disco.y - mouse_y
                            break # Encontrou o disco, pode parar de procurar

        # 2. MOVENDO O MOUSE
        elif evento.type == pygame.MOUSEMOTION:
            if disco_arrastado is not None:
                # Atualiza a posição do retângulo do disco de acordo com o mouse
                rect_arrastado.x = mouse_x + offset_x
                rect_arrastado.y = mouse_y + offset_y

        # 3. SOLTOU O BOTÃO DO MOUSE
        elif evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 1 and disco_arrastado is not None:
                # Determinar em qual pino o mouse está soltando (dividi a tela em 3 colunas)
                pino_destino = None
                if mouse_x < 300: pino_destino = "A"
                elif mouse_x < 533: pino_destino = "B"
                else: pino_destino = "C"
                
                # Validação da regra da Torre de Hanói
                discos_destino = torres[pino_destino]
                
                # É válido se a torre estiver vazia ou se o disco do topo for MAIOR que o arrastado
                movimento_valido = len(discos_destino) == 0 or discos_destino[-1] > disco_arrastado
                
                if movimento_valido:
                    torres[pino_destino].append(disco_arrastado)
                    if pino_destino != pino_origem: # Só conta movimento se trocou de pino
                        movimentos += 1
                    if len(torres["C"]) == num_discos:
                        venceu = True
                        tempo_final = pygame.time.get_ticks()
                else:
                    # Movimento inválido! Devolve o disco para o pino de origem
                    torres[pino_origem].append(disco_arrastado)
                
                # Reseta as variáveis de arrastar
                disco_arrastado = None
                rect_arrastado = None
                pino_origem = None

    # --- DESENHANDO NA TELA ---
    tela.fill(BRANCO)

    if estado == "menu":
        titulo = fonte_titulo.render("Torre de Hanói", True, AZUL_ESCURO)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 140)))

        desenhar_botao(BOTAO_INICIAR, "Iniciar", VERDE)
        desenhar_botao(BOTAO_REGRAS, "Regras")

        rotulo = fonte.render("Número de discos", True, AZUL_ESCURO)
        tela.blit(rotulo, rotulo.get_rect(center=(LARGURA // 2, 440)))
        desenhar_botao(BOTAO_MENOS, "-")
        desenhar_botao(BOTAO_MAIS, "+")
        valor = fonte_titulo.render(str(num_discos), True, AZUL_ESCURO)
        tela.blit(valor, valor.get_rect(center=(LARGURA // 2, 495)))

    elif estado == "regras":
        titulo = fonte_titulo.render("Regras", True, AZUL_ESCURO)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 80)))
        for i, linha in enumerate(REGRAS):
            tela.blit(fonte.render(linha, True, AZUL_ESCURO), (50, 160 + i * 38))
        desenhar_botao(BOTAO_VOLTAR, "Voltar")

    else:
        # Textos (Timer e Contador)
        tempo_atual = tempo_final if venceu else pygame.time.get_ticks()
        tempo_decorrido = (tempo_atual - tempo_inicial) // 1000
        texto_timer = f"Tempo: {tempo_decorrido // 60:02d}:{tempo_decorrido % 60:02d}"
        
        tela.blit(fonte.render(texto_timer, True, AZUL_ESCURO), (20, 20))
        tela.blit(fonte.render(f"Movimentos: {movimentos}", True, AZUL_ESCURO), (20, 60))
        meta = 2 ** num_discos - 1
        tela.blit(fonte.render(f"Meta: {meta} Movimentos", True, CINZA), (LARGURA - 290, 20))

        # Base e Pinos
        pygame.draw.rect(tela, CINZA, (100, 500, 600, 20)) # Base (Chão)
        for pino_x in CENTROS_X.values():
            pygame.draw.rect(tela, CINZA, (pino_x - 10, 280, 20, 220)) # Pinos verticais

        # Discos que estão encaixados nos pinos
        for pino, discos in torres.items():
            for indice, tamanho in enumerate(discos):
                largura = largura_disco(tamanho)
                x = CENTROS_X[pino] - (largura // 2)
                # O Y sobe conforme o índice na lista aumenta (empilhando)
                y = CHAO_Y - ((indice + 1) * ALTURA_DISCO)
                
                # Desenha com cantos arredondados (border_radius=5)
                pygame.draw.rect(tela, CORES_DISCOS[tamanho], (x, y, largura, ALTURA_DISCO), border_radius=5)

        # Desenha o disco que está sendo arrastado (por cima de todos)
        if disco_arrastado is not None:
            pygame.draw.rect(tela, CORES_DISCOS[disco_arrastado], rect_arrastado, border_radius=5)

        # Tela de vitória
        if venceu:
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((44, 62, 80, 190))
            tela.blit(overlay, (0, 0))
            texto = fonte_grande.render("Você Venceu!", True, VERDE)
            tela.blit(texto, texto.get_rect(center=(LARGURA // 2, ALTURA // 2 - 40)))
            resumo = fonte.render(f"{texto_timer}  |  Movimentos: {movimentos}", True, BRANCO)
            tela.blit(resumo, resumo.get_rect(center=(LARGURA // 2, ALTURA // 2 + 30)))

        # Botões (por cima do overlay de vitória)
        desenhar_botao(BOTAO_REINICIAR, "Reiniciar")
        desenhar_botao(BOTAO_MENU, "Menu")

    pygame.display.flip()
    clock.tick(60)