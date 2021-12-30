import pygame
from pygame.locals import *
import json

pygame.init()

largura = 650
altura = 700
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Breakout')

# variaveis do jogo
colunas = 11
linhas = 9
relogio = pygame.time.Clock()
bola = False
inicio = True
jogo = False
game_over = 0
vidas = 3
pontos = 0
partida = 0

# sons do jogo
wall_hit = pygame.mixer.Sound('wall_hit.wav')
block_hit = pygame.mixer.Sound('block_hit.wav')

# tela inicial
start_img = pygame.image.load('logo.png')
botao1 = pygame.Rect(200, 320, 200, 60)
botao2 = pygame.Rect(200, 400, 200, 60)
botao3 = pygame.Rect(200, 480, 200, 60)
game_fonte1 = pygame.font.Font('atari_font.ttf', 25)
texto1 = game_fonte1.render('iniciar', True, (225, 225, 225))
texto2 = game_fonte1.render('pontuações', True, (225, 225, 225))
texto3 = game_fonte1.render('sair', True, (225, 225, 225))
game_fonte2 = pygame.font.Font('atari_font.ttf', 20)
game_fonte3 = pygame.font.Font('atari_font.ttf', 30)

# dados
dados = {'primeiro': 0, '1nome': '', 'segundo': 0, '2nome': '', 'terceiro': 0, '3nome': ''}
try:
    with open('pontos_do_jogador1.txt') as arquivo:
        dados = json.load(arquivo)
except:
    print('sem arquivo')


class wall():  # parede de blocos
    def __init__(self):
        self.width = largura // colunas
        self.height = 20

    def create_wall(self):
        self.blocks = []
        block_individual = []  # lista vazia para os blocos individuais
        for row in range(linhas):
            block_row = []  # reseta a fileira de blocos
            for col in range(colunas):
                block_x = col * self.width
                block_y = row * self.height + 50
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                if row < 3:
                    strength = 3
                elif row < 6:
                    strength = 2
                elif row < 9:
                    strength = 1
                blocos_individuais = [rect, strength]
                block_row.append(blocos_individuais)
            self.blocks.append(block_row)

    def draw_wall(self):  # desenha a parede de blocos
        for row in self.blocks:
            for block in row:
                if block[1] == 3:
                    block_col = (225, 0, 0)
                elif block[1] == 2:
                    block_col = (0, 200, 0)
                elif block[1] == 1:
                    block_col = (225, 200, 0)
                pygame.draw.rect(tela, block_col, block[0])
                pygame.draw.rect(tela, (10, 10, 10), (block[0]), 5)


class paddle():  # peça do jogador
    def __init__(self):
        self.reset()

    def move(self):  # movimento da peça do jogador
        self.direction = 0
        chave = pygame.key.get_pressed()
        if chave[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        if chave[pygame.K_RIGHT] and self.rect.right < largura:
            self.rect.x += self.speed
            self.direction = 1

    def draw(self):  # desenha a peça do jogador
        pygame.draw.rect(tela, (0, 20, 225), self.rect)

    def reset(self):
        self.height = 20
        self.width = 100
        self.x = int((largura / 2) - (self.width / 2))
        self.y = altura - (self.height * 2)
        self.speed = 10
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0


class game_ball():  # bola do jogo
    def __init__(self, x, y):
        self.reset(x, y)

    def move(self):  # movimento da bola
        colisao = 5
        global pontos
        global dados
        # colisão com a parede de blocos
        wall_destroyed = 1
        row_count = 0
        for row in wall.blocks:
            item_count = 0
            for item in row:
                if self.rect.colliderect(item[0]):
                    if abs(self.rect.bottom - item[0].top) < colisao and self.speed_y > 0:
                        self.speed_y *= -1
                    if abs(self.rect.top - item[0].bottom) < colisao and self.speed_y < 0:
                        self.speed_y *= -1
                    if abs(self.rect.right - item[0].left) < colisao and self.speed_x > 0:
                        self.speed_x *= -1
                    if abs(self.rect.left - item[0].right) < colisao and self.speed_x < 0:
                        self.speed_y *= -1

                    # reduz a dureza do bloco ao receber dano
                    if wall.blocks[row_count][item_count][1] > 1:
                        wall.blocks[row_count][item_count][1] -= 1
                        wall_hit.play()
                    else:
                        wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)
                        pontos += 10
                        block_hit.play()

                # verifica se o bloco ainda existe
                if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0
                item_count += 1  # aumenta o contador
            row_count += 1  # aumenta o contador das colunas
        if wall_destroyed == 1:  # verifica se a parede foi destruída
            self.game_over = 1

        # colisão com a parede
        if self.rect.left < 0 or self.rect.right > largura:
            self.speed_x *= -1
            wall_hit.play()
        # colisão com o topo e a base da tela
        if self.rect.top < 0:
            self.speed_y *= -1
            wall_hit.play()
        if self.rect.bottom > altura:
            self.game_over = -1
        # colisão com a peça do jogador
        if self.rect.colliderect(peca_do_jogador):
            if abs(self.rect.bottom - peca_do_jogador.rect.top) < colisao and self.speed_y > 0:
                wall_hit.play()
                self.speed_y *= -1
                self.speed_x += peca_do_jogador.direction
                if self.speed_x > self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                    self.speed_x = -self.speed_max
            else:
                self.speed_x *= -1

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.game_over

    def draw(self):  # desenhando a bola
        pygame.draw.circle(tela, (255, 255, 255),
                           (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)

    def reset(self, x, y):
        self.ball_rad = 8
        self.x = x - self.ball_rad
        self.y = y
        self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = 4
        self.speed_y = -4
        self.speed_max = 7
        self.game_over = 0


def placar():
    start_img1 = pygame.image.load('logo.png')
    tela.blit(start_img1, (40, 60))
    titulo = game_fonte3.render('Maiores pontuações', True, (225, 0, 0))
    tela.blit(titulo, (60, 250))
    primeiro = game_fonte1.render('1º: ' + f'{dados["1nome"]} {dados["primeiro"]} pontos', True, (225, 225, 225))
    tela.blit(primeiro, (50, 350))
    segundo = game_fonte1.render('2º: ' + f'{dados["2nome"]} {dados["segundo"]} pontos', True, (225, 225, 225))
    tela.blit(segundo, (50, 450))
    terceiro = game_fonte1.render('3º: ' + f'{dados["3nome"]} {dados["terceiro"]} pontos', True, (225, 225, 225))
    tela.blit(terceiro, (50, 550))


def tela_final():
    start_img1 = pygame.image.load('logo.png')
    tela.blit(start_img1, (40, 60))
    texto_score = game_fonte1.render('Pontuação atingida: ' + str(partida), True, (225, 225, 225))
    tela.blit(texto_score, (20, 250))
    texto_score = game_fonte1.render('Digite seu nome: ', True, (225, 225, 225))
    tela.blit(texto_score, (20, 350))


def lives():
    texto_score = game_fonte3.render('0' + str(vidas), True, (225, 225, 225))
    texto_score2 = game_fonte3.render(str(pontos), True, (225, 225, 225))
    tela.blit(texto_score, (35, 10))
    tela.blit(texto_score2, (450, 10))


def draw_text():
    texto01 = game_fonte2.render('CLIQUE NA TELA PARA COMEÇAR', True, (225, 225, 225))
    texto04 = game_fonte2.render('VOCÊ PERDEU!', True, (225, 225, 225))
    texto05 = game_fonte2.render('CLIQUE NA TELA PARA RECOMEÇAR', True, (225, 225, 225))
    if game_over == 0:
        tela.blit(texto01, (60, altura // 2 + 100))
    elif game_over == -1 and vidas == 0:
        tela.blit(texto04, (220, altura // 2 + 50))
        tela.blit(texto05, (45, altura // 2 + 100))


def pontuacao():
    if pontos > dados['primeiro']:
        dados['terceiro'] = dados['segundo']
        dados['segundo'] = dados['primeiro']
        dados['primeiro'] = pontos
        dados['3nome'] = dados['2nome']
        dados['2nome'] = dados['1nome']
        dados['1nome'] = str(nome)
        with open('pontos_do_jogador1.txt', 'w') as arquivo:
            json.dump(dados, arquivo)
    elif dados['primeiro'] > pontos > dados['segundo']:
        dados['terceiro'] = dados['segundo']
        dados['segundo'] = pontos
        dados['3nome'] = dados['2nome']
        dados['2nome'] = str(nome)
        with open('pontos_do_jogador1.txt', 'w') as arquivo:
            json.dump(dados, arquivo)
    elif dados['segundo'] > pontos > dados['terceiro']:
        dados['terceiro'] = pontos
        dados['3nome'] = str(nome)
        with open('pontos_do_jogador1.txt', 'w') as arquivo:
            json.dump(dados, arquivo)


input_name = ''
input_rect = pygame.Rect(20, 400, 140, 32)
nome = ''

# ativa a parede de blocos, a bola e a peça do jogador
wall = wall()
wall.create_wall()
peca_do_jogador = paddle()
ball = game_ball(peca_do_jogador.x + (peca_do_jogador.width // 2), peca_do_jogador.y - peca_do_jogador.height)

run = True
while run:  # loop do jogo
    relogio.tick(60)

    if inicio == True and jogo == False:
        tela.fill((0, 0, 0))
        tela.blit(start_img, (40, 60))
        pygame.draw.rect(tela, [0, 0, 0], botao1)
        tela.blit(texto1, (240, 320))
        pygame.draw.rect(tela, [0, 0, 0], botao2)
        tela.blit(texto2, (200, 400))
        pygame.draw.rect(tela, [0, 0, 0], botao3)
        tela.blit(texto3, (270, 480))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if botao1.collidepoint(mouse_pos):
                    inicio = False
                    jogo = True
                elif botao2.collidepoint(mouse_pos):
                    inicio = True
                    jogo = True
                elif botao3.collidepoint(mouse_pos):
                    run = False

    if inicio == False and jogo == False:
        tela.fill((0, 0, 0))
        tela_final()
        text_surface = game_fonte1.render(input_name, True, (225, 225, 225))
        pygame.draw.rect(tela, (225, 0, 0), input_rect, 2)
        tela.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        input_rect.w = max(100, text_surface.get_width() + 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_name = input_name[:-1]
                elif event.key == pygame.K_KP_ENTER:
                    nome = input_name
                    pontuacao()
                    with open('pontos_do_jogador1.txt', 'w') as arquivo:
                        json.dump(dados, arquivo)
                    input_name = ''
                    pontos = 0
                    inicio = False
                    jogo = True
                else:
                    input_name += event.unicode

    if inicio == True and jogo == True:
        tela.fill((0, 0, 0))
        placar()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    inicio = True
                    jogo = False

    if inicio == False and jogo == True:
        tela.fill((10, 10, 10))
        wall.draw_wall()
        ball.draw()
        peca_do_jogador.draw()
        lives()

        if bola:
            peca_do_jogador.move()
            game_over = ball.move()
            if game_over != 0:
                bola = False

        elif not bola:
            draw_text()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and bola == False:
                bola = True
                ball.reset(peca_do_jogador.x + (peca_do_jogador.width // 2), peca_do_jogador.y - peca_do_jogador.height)
                peca_do_jogador.reset()
            if event.type == pygame.MOUSEBUTTONDOWN and game_over == -1:
                vidas -= 1
                if vidas < 0:
                    partida = pontos
                    vidas = 3
                    inicio = False
                    jogo = False
                    wall.create_wall()
            if event.type == pygame.MOUSEBUTTONDOWN and game_over == 1:
                ball.reset(peca_do_jogador.x + (peca_do_jogador.width // 2),
                           peca_do_jogador.y - peca_do_jogador.height)
                peca_do_jogador.reset()
                wall.create_wall()
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    ball.reset(peca_do_jogador.x + (peca_do_jogador.width // 2),
                               peca_do_jogador.y - peca_do_jogador.height)
                    peca_do_jogador.reset()
                    wall.create_wall()
                    inicio = True
                    jogo = False

    pygame.display.update()  # ativa o preenchimento de cor na tela

pygame.quit()
