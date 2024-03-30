#Coded by Alex Behm, 3/29/2024

#Sources:
#Font created by Steve Matteson: https://fonts.google.com/specimen/Open+Sans/about
#Character Piece Art: "https://www.flaticon.com/free-icons/pawn" title="pawn icons">Pawn icons created by smashingstocks - Flaticon
#Game sound effects: https://mixkit.co/free-sound-effects/game/
#External Modules Used: Pygame: https://www.pygame.org/docs/ Numpy: https://numpy.org/doc/ Pathfinding: https://pypi.org/project/pathfinding/
#Game Inspiration: https://en.wikipedia.org/wiki/Quoridor

import pygame, sys, copy, re, random
import numpy as np
from pygame import mixer

#______________________PATHFINDING MODULES____________________
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# _____________________SCREEN INITIATION_______________________
pygame.init()
SCREEN_SIZE = 750
GRID_SIZE = 600
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption('Blockade')

#________________________COLORS_________________________________
bg_color = (43,43,43)
square_color = (30,30,30)
selected_square_color = (50,50,50)
shadow_color = (20,20,20)
text_color = (255,255,255)
transparent_color = (0, 0, 0, 128) 
wall_color = (173, 110, 0)
side_wall_color = (115, 73, 0)
player_colors = [(0,185,12),(255,0,0),(0,153,217),(249,236,0)] #Player 1, 2, 3, 4

#________________________IMAGE LOADING__________________________
player_images = [pygame.image.load('images/pawn1.png'),pygame.image.load('images/pawn2.png'),pygame.image.load('images/pawn3.png'),pygame.image.load('images/pawn4.png')]
pygame.display.set_icon(player_images[0])

#________________________FONTS______________________________
countFont = pygame.font.Font('fonts/gameFont.ttf', 32)
turnFont = pygame.font.Font('fonts/gameFont.ttf', 20)
titleFont = pygame.font.Font('fonts/titleFont.ttf', 54)
winnerFont = pygame.font.Font('fonts/titleFont.ttf', 30)
smallFont = pygame.font.Font('fonts/titleFont.ttf', 15)     

#_______________________SOUNDS______________________________
pieceMoveSound = mixer.Sound('sounds/PieceMove.mp3')
pieceMoveSound.set_volume(0.4)
wallPlaceSound = mixer.Sound('sounds/wallMove.mp3')
wallPlaceSound.set_volume(0.4)
buttonSound = mixer.Sound('sounds/buttonSound.mp3')
buttonSound.set_volume(0.2)

#________________________BOARDS______________________________
BOARD_SIZE = 9
VERT_WALL_ROWS = 9
VERT_WALL_COLS = 8
HORI_WALL_COLS = 9
HORI_WALL_ROWS = 8
space_board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
vert_wall_board = np.zeros((VERT_WALL_ROWS, VERT_WALL_COLS), dtype=int)
hori_wall_board = np.zeros((HORI_WALL_ROWS, HORI_WALL_COLS), dtype=int)
#________________________WALL/TURN/PLAYER COUNT_________________________
wall_counts = [10,10,10,10]
turn = 1
numPlayers = 2
#__________BUTTON POSITION HOLDERS___________________________
vertWallPositions = []
horiWallPositions = []
menuButtonPositions = []
menuButtonHover = 0
optionsButtonPositions = []
optionsButtonHover = []
selectButtonPositions = []
selectButtonHover = []
instructionButtonPositions = []
instructionButtonHover = []

menu = 0 #- Controls menu (0 = main menu, 1 = game screen, 2 = winner popup, 3 = Player Select Menu, 4 = options menu, 5 = instructions menu)

playingAI = False
#________________________PATHFINDING_________________________
visited = []
pathIterations = 0

def drawText(x, y, text, font, color):

    #Allows text to be drawn at the specified x and y coordinate with the specified font and color

    text_render = font.render(text, True, color)
    text_rect = text_render.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_render, text_rect)

def themeSelect(theme):

    #Allows the specified theme to be switched

    global bg_color, square_color, selected_square_color, shadow_color, text_color, transparent_color, side_wall_color, wall_color

    #_______________LIGHT THEME____________________
    if theme == 'light':
        bg_color = (210, 210, 210)
        square_color = (190, 190, 190)
        selected_square_color = (225, 225, 225)
        shadow_color = (160,160,160)
        text_color = (255,255,255)
        transparent_color = (255, 255, 255, 100)
        wall_color = (255, 197, 115)
        side_wall_color = ((222, 170, 98))
    #_______________DARK THEME____________________
    if theme == 'dark':
        bg_color = (43,43,43)
        square_color = (30,30,30)
        selected_square_color = (50,50,50)
        shadow_color = (20,20,20)
        text_color = (255,255,255)
        transparent_color = (0, 0, 0, 100)
        wall_color = (173, 110, 0)
        side_wall_color = (115, 73, 0)

def createMenu():

    #Draws the main menu on the screen

    global menuButtonHover
    #_____________DRAW MAIN MENU BUTTONS____________________
    buttons = ['Play','Instructions','Options','Quit']
    for index in range(0,4):
        button_string = buttons[index]
        button_render = turnFont.render(button_string, True, text_color)
        button_y  = (SCREEN_SIZE - 70)/2 + index * 100 - 50
        button_x = (SCREEN_SIZE - 200)/2
        button_rect = pygame.Rect(button_x, button_y, 200, 70)
        text_rect = button_render.get_rect(center=button_rect.center)
        if button_rect not in menuButtonPositions:
            menuButtonPositions.append(button_rect)
        if index == menuButtonHover:
            pygame.draw.rect(screen, player_colors[0], button_rect)
        else:
            pygame.draw.rect(screen, square_color, button_rect)
        screen.blit(button_render, text_rect)
    #___________DRAW GAME TITLE AND LOGO___________________
    drawText(SCREEN_SIZE/2, 100, 'BLOCKADE', titleFont, text_color)

def createOptionsMenu():

    #Draws the options menu on the screen

    global optionsButtonHover
    #_____________DRAW OPTION MENU BUTTONS____________________
    buttons = ['Light','Dark','Back']
    for index in range(0,len(buttons)):
        button_string = buttons[index]
        button_render = turnFont.render(button_string, True, text_color)
        if index < len(buttons) - 1:
            button_y  = (SCREEN_SIZE - 40)/2 + index * 50 - 130
            button_x = (SCREEN_SIZE - 150)/2
        else:
            button_y  = SCREEN_SIZE - 70
            button_x = 20
        button_rect = pygame.Rect(button_x, button_y, 150, 40)
        text_rect = button_render.get_rect(center=button_rect.center)
        if button_rect not in optionsButtonPositions:
            optionsButtonPositions.append(button_rect)
        if index == optionsButtonHover:
            pygame.draw.rect(screen, player_colors[0], button_rect)
        else:
            pygame.draw.rect(screen, square_color, button_rect)
        screen.blit(button_render, text_rect)
    #___________DRAW GAME TITLE AND LOGO___________________
    drawText(SCREEN_SIZE/2, 100, 'OPTIONS', titleFont, text_color)
    drawText(SCREEN_SIZE/2, 200, 'GAME THEMES', smallFont, text_color)

def createInstructionsMenu():

    #Draws the instructions menu on the screen

    global instructionButtonHover
    #_____________DRAW OPTION MENU BUTTONS____________________
    buttons = ['Back']
    for index in range(0,len(buttons)):
        button_string = buttons[index]
        button_render = turnFont.render(button_string, True, text_color)
        button_y  = SCREEN_SIZE - 70
        button_x = 20
        button_rect = pygame.Rect(button_x, button_y, 150, 40)
        text_rect = button_render.get_rect(center=button_rect.center)
        if button_rect not in instructionButtonPositions:
            instructionButtonPositions.append(button_rect)
        if index == instructionButtonHover:
            pygame.draw.rect(screen, player_colors[0], button_rect)
        else:
            pygame.draw.rect(screen, square_color, button_rect)
        screen.blit(button_render, text_rect)
    #___________DRAW GAME TITLE AND LOGO___________________
    drawText(SCREEN_SIZE/2, 70, 'Instructions', titleFont, text_color)
    drawText(SCREEN_SIZE/2, 150, 'Blockade is a 2-4 player game based on the game Quirrodor. The Rules are as follows:', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 180, 'GOAL', turnFont, player_colors[0])
    drawText(SCREEN_SIZE/2, 200, '- The goal of the game is to move your pawn to the opposite side of the board first.', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 220, '- This means a player who starts on the leftmost side of the board wins by getting their', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 240, 'pawn to any square on the rightmost side of the board.', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 280, 'WHAT TO DO ON EACH TURN', turnFont, player_colors[0])
    drawText(SCREEN_SIZE/2, 300, '- The current players turn has their pawn highlighted on the board.', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 320, '- During a player\'s turn, they may either place one wall or move their pawn once.', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 360, 'PLACING WALLS', turnFont, player_colors[0])
    drawText(SCREEN_SIZE/2, 380, '- Walls can be placed to impede your opponents path.', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 400, '- Walls can be placed horizontally or vertically between spaces by using', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 420, 'the mouse to click on the desired space.', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 440, '- A maximum of ten walls can be placed in a round and the amount of walls', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 460, 'a player has left is indicated on the side of the board they started on (The brown rectangles).', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 480, '- NOTICE: Walls can not be placed in a way that entirely blocks of a player\'s path to their', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 500, 'opposite side and the game will not allow some walls to be placed to prevent this.', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 540, 'MOVEMENT', turnFont, player_colors[0])
    drawText(SCREEN_SIZE/2, 560, '- Players can move their pawn up, down, left or right using the respective arrow keys.', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 580, '- Players can not move their pawn diagonally or through a wall to get to a space.', smallFont, text_color)
    drawText(SCREEN_SIZE/2, 620, '- NOTE: You can press [Escape] any time to return to the main menu.', smallFont, text_color)

def createPlayerSelectMenu():

    # Draws the select number of players menu

    global selectButtonHover
    #_____________DRAW OPTION MENU BUTTONS____________________
    buttons = ['Two','Three','Four','Computer','Back']
    for index in range(0,len(buttons)):
        button_string = buttons[index]
        button_render = turnFont.render(button_string, True, text_color)
        if index < len(buttons) - 1:
            button_y  = (SCREEN_SIZE - 40)/2 + index * 50 - 130
            button_x = (SCREEN_SIZE - 150)/2
        else:
            button_y  = SCREEN_SIZE - 70
            button_x = 20
        button_rect = pygame.Rect(button_x, button_y, 150, 40)
        text_rect = button_render.get_rect(center=button_rect.center)
        if button_rect not in selectButtonPositions:
            selectButtonPositions.append(button_rect)
        if index == selectButtonHover:
            pygame.draw.rect(screen, player_colors[0], button_rect)
        else:
            pygame.draw.rect(screen, square_color, button_rect)
        screen.blit(button_render, text_rect)
    #___________DRAW GAME TITLE AND LOGO___________________
    drawText(SCREEN_SIZE/2, 100, 'PLAYER SELECT', titleFont, text_color)
    drawText(SCREEN_SIZE/2, 200, 'SELECT AMOUNT OF PLAYERS', smallFont, text_color)

def createGameVisuals(turn):

    #Draws the main visuals for the game (The board, walls, pieces)

    #________________________DRAW SPACES____________________
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            rect_x = ((SCREEN_SIZE - GRID_SIZE)/2) + col * (56 + 12)
            rect_y = ((SCREEN_SIZE - GRID_SIZE)/2) + row * (56 + 12)
            space = pygame.Rect(rect_x, rect_y, 54, 54)
            if space_board[row][col] == turn:
                pygame.draw.rect(screen, selected_square_color, space)
            else:
                pygame.draw.rect(screen, square_color, space)
            #________________DRAW PLAYER PIECES_____________
            for player in range(0,numPlayers):
                if space_board[row][col] == player + 1:
                    img_space = pygame.Rect(space.center[0]-23,space.center[1]-23,1,1)
                    screen.blit(player_images[player], img_space)
    
    #________________________DRAW SHADOWS_____________________
    for row in range(HORI_WALL_ROWS + 1):
        for col in range(HORI_WALL_COLS):
            shadow = pygame.Rect(((SCREEN_SIZE - GRID_SIZE)/2) + col * (56 + 12), (((SCREEN_SIZE - GRID_SIZE)/2) + row * (56 + 12)) + 54, 54,5)
            pygame.draw.rect(screen, shadow_color, shadow)
    #________________________DRAW VERTICAL WALLS____________________
    for row in range(VERT_WALL_ROWS):
        for col in range(VERT_WALL_COLS):
            if vert_wall_board[row][col] == 1:
                start_point = ((((SCREEN_SIZE - GRID_SIZE)/2) + col * (56 + 12)) + 60, ((SCREEN_SIZE - GRID_SIZE)/2) + row * (56 + 12) - 25)
                end_point = ((((SCREEN_SIZE - GRID_SIZE)/2) + col * (56 + 12)) + 60, ((SCREEN_SIZE - GRID_SIZE)/2) + row * (56 + 12) + 28)
                wall_side_rect = pygame.Rect((((SCREEN_SIZE - GRID_SIZE)/2) + col * (56 + 12)) + 58, ((SCREEN_SIZE - GRID_SIZE)/2) + row * (56 + 12) + 28, 6,25)
                line_thickness = 6
                pygame.draw.line(screen, wall_color, start_point, end_point, line_thickness)
                pygame.draw.rect(screen, side_wall_color, wall_side_rect)
        
    #_______________________DRAW HORIZONTAL WALLS___________________
    for row in range(HORI_WALL_ROWS):
        for col in range(HORI_WALL_COLS):
            if hori_wall_board[row][col] == 1:
                start_point = (((SCREEN_SIZE - GRID_SIZE)/2) + col * (56 + 12), (((SCREEN_SIZE - GRID_SIZE)/2) + row * (56 + 12)) + 35)
                end_point = ((((SCREEN_SIZE - GRID_SIZE)/2) + col * (56 + 12)) + 53, (((SCREEN_SIZE - GRID_SIZE)/2) + row * (56 + 12)) + 35)
                wall_side_rect = pygame.Rect(((SCREEN_SIZE - GRID_SIZE)/2) + col * (56 + 12), (((SCREEN_SIZE - GRID_SIZE)/2) + row * (56 + 12)) + 35, 54,25)
                line_thickness = 6
                pygame.draw.rect(screen, side_wall_color, wall_side_rect)
                pygame.draw.line(screen, wall_color, start_point, end_point, line_thickness)
    #______________________DRAW WALL COUNTS_________________________
    if menu != 2:
        for wall in range(wall_counts[0]):
            rect_x = 9
            rect_y = wall * 40 + 180
            wall_rect = pygame.Rect(rect_x, rect_y, 56, 6)
            side_wall_rect = pygame.Rect(rect_x, rect_y + 6, 56, 25)
            pygame.draw.rect(screen, wall_color, wall_rect)
            pygame.draw.rect(screen, side_wall_color, side_wall_rect)

        for wall in range(wall_counts[1]):
            rect_x = SCREEN_SIZE - 65
            rect_y = wall * 40 + 180
            wall_rect = pygame.Rect(rect_x, rect_y, 56, 6)
            side_wall_rect = pygame.Rect(rect_x, rect_y + 6, 56, 25)
            pygame.draw.rect(screen, wall_color, wall_rect)
            pygame.draw.rect(screen, side_wall_color, side_wall_rect)

        if numPlayers > 2:
            for wall in range(wall_counts[2]):
                rect_x = wall * 40 + 180
                rect_y = SCREEN_SIZE - 65
                wall_rect = pygame.Rect(rect_x, rect_y, 6, 56)
                side_wall_rect = pygame.Rect(rect_x, rect_y+56, 6, 25)
                pygame.draw.rect(screen, wall_color, wall_rect)
                pygame.draw.rect(screen, side_wall_color, side_wall_rect)

        if numPlayers > 3:
            for wall in range(wall_counts[3]):
                rect_x = wall * 40 + 180
                rect_y = -12
                wall_rect = pygame.Rect(rect_x, rect_y, 6, 56)
                side_wall_rect = pygame.Rect(rect_x, rect_y+56, 6, 25)
                pygame.draw.rect(screen, wall_color, wall_rect)
                pygame.draw.rect(screen, side_wall_color, side_wall_rect)

def drawWinScreen(player):

    #Draws the win screen to indicate which player won

    global menu
    menu = 2
    surface_width, surface_height = 200, 100
    surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
    surface.fill(transparent_color)
    screen.blit(surface, ((SCREEN_SIZE-200)/2, (SCREEN_SIZE-100)/2))
    drawText(SCREEN_SIZE/2,SCREEN_SIZE/2,'WIN', titleFont, player_colors[int(player) - 1])
    drawText(SCREEN_SIZE/2,SCREEN_SIZE - 40,'PRESS [ESCAPE] TO GO TO MAIN MENU', smallFont, text_color)

def createHitboxes():

    #Adds the position of both vertical and horizontal wall rects to a list so that it is easy to verify if they are clicked on

    #________________VERTICAL WALL HITBOXES__________________________
    for row in range(VERT_WALL_ROWS):
        for col in range(VERT_WALL_COLS):
            vertWallHitboxRect = pygame.Rect((((SCREEN_SIZE - GRID_SIZE)/2) + col * (56 + 12)) + 54, ((SCREEN_SIZE - GRID_SIZE)/2) + row * (56 + 12), 15,54)
            vertWallPositions.append(vertWallHitboxRect)
    #________________HORIZONTAL WALL HITBOXES__________________________
    for row in range(HORI_WALL_ROWS):
        for col in range(HORI_WALL_COLS):
            horiWallHitboxRect = pygame.Rect(((SCREEN_SIZE - GRID_SIZE)/2) + col * (56 + 12), (((SCREEN_SIZE - GRID_SIZE)/2) + row * (56 + 12)) + 54, 54,15)
            horiWallPositions.append(horiWallHitboxRect)

def checkWin():

    #Checks if there are any winners on the board and signals the win screen text to be drawn
    #Returns true if there is a winner

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if space_board[row][col] == 1 and col == 8: #Player 1 Wins
                drawWinScreen('1')
                return True
            if space_board[row][col] == 2 and col == 0: #Player 2 Wins
                drawWinScreen('2')
                return True
            if space_board[row][col] == 3 and row == 0: #Player 3 Wins
                drawWinScreen('3')
                return True
            if space_board[row][col] == 4 and row == 8: #Player 4 Wins
                drawWinScreen('4')
                return True

def placeWall(isVertical, row, col):

    #Places a wall on the board in the specified row or column
    #Returns true for a succesful placement

    global wall_counts, turn
    if isVertical:
        if wall_counts[turn - 1] > 0 and vert_wall_board[row][col] == 0:
            if isPath(row, col, True):
                wallPlaceSound.play()
                vert_wall_board[row][col] = 1
                wall_counts[turn - 1] -= 1
                turn += 1
                return True
    if not isVertical:
        if wall_counts[turn - 1] > 0 and hori_wall_board[row][col] == 0:
            if isPath(row, col, False):
                wallPlaceSound.play()
                hori_wall_board[row][col] = 1
                wall_counts[turn - 1] -= 1
                turn += 1
                return True
        
def inputHandler():

    #Handles the input for the entire game (Arrow keys, mouse clicks, escape key, buttons pressed on menus)
    #Also handles the button click sounds and current menu variables

    global turn, wall_counts, menuButtonHover, menu, optionsButtonHover, numPlayers, selectButtonHover, playingAI, instructionButtonHover, turn
    for event in pygame.event.get():
        pos = pygame.mouse.get_pos()
        #_____________________CHECKS IF MAIN MENU BUTTONS ARE HOVERED_____________________
        if menu == 0:
            for rect in menuButtonPositions:
                if rect.collidepoint(pos):
                    menuButtonHover = menuButtonPositions.index(rect)
                    #__________________PLAY BUTTON ARE PRESSED_______________________________
                    if event.type == pygame.MOUSEBUTTONUP and menuButtonHover == 0:
                        buttonSound.play()
                        menu = 3
                        return
                    #__________________INSTRUCTIONS BUTTON IS PRESSED_______________________________
                    if event.type == pygame.MOUSEBUTTONUP and menuButtonHover == 1:
                        buttonSound.play()
                        menu = 5
                        return
                    #__________________OPTIONS BUTTON ARE PRESSED___________________________
                    if event.type == pygame.MOUSEBUTTONUP and menuButtonHover == 2:
                        buttonSound.play()
                        menu = 4
                        return
                    #__________________QUIT BUTTON ARE PRESSED_______________________________
                    if event.type == pygame.MOUSEBUTTONUP and menuButtonHover == 3:
                        buttonSound.play()
                        sys.exit()
        #___________________CHECKS IF SELECT MENU BUTTONS ARE ARE PRESSED___________________
        if menu == 3:
            for rect in selectButtonPositions:
                if rect.collidepoint(pos):
                    selectButtonHover = selectButtonPositions.index(rect)
                    #__________________TWO PLAYERS BUTTON PRESSED_______________________________
                    if event.type == pygame.MOUSEBUTTONUP and selectButtonHover == 0:
                        buttonSound.play()
                        resetBoard()
                        numPlayers = 2
                        menu = 1
                        playingAI = False
                        main()
                        return
                    #__________________THREE PLAYERS BUTTON PRESSED___________________________
                    if event.type == pygame.MOUSEBUTTONUP and selectButtonHover == 1:
                        buttonSound.play()
                        resetBoard()
                        numPlayers = 3
                        menu = 1
                        playingAI = False
                        main()
                        return
                    #__________________FOUR PLAYERS BUTTON PRESSED___________________________
                    if event.type == pygame.MOUSEBUTTONUP and selectButtonHover == 2:
                        buttonSound.play()
                        resetBoard()
                        numPlayers = 4
                        menu = 1
                        playingAI = False
                        main()
                        return
                    #__________________AI BUTTON PRESSED___________________________
                    if event.type == pygame.MOUSEBUTTONUP and selectButtonHover == 3:
                        buttonSound.play()
                        resetBoard()
                        turn = 2
                        numPlayers = 2
                        playingAI = True
                        menu = 1
                        main()
                        return
                        
                    #__________________BACK BUTTON PRESSED_______________________________
                    if event.type == pygame.MOUSEBUTTONUP and selectButtonHover == 4:
                        buttonSound.play()
                        menu = 0
                        mainMenu()
                        return
                    
        #___________________CHECKS IF OPTION MENU BUTTONS ARE ARE PRESSED___________________
        if menu == 4:
            for rect in optionsButtonPositions:
                if rect.collidepoint(pos):
                    optionsButtonHover = optionsButtonPositions.index(rect)
                    #__________________LIGHT THEME BUTTON PRESSED_______________________________
                    if event.type == pygame.MOUSEBUTTONUP and optionsButtonHover == 0:
                        buttonSound.play()
                        themeSelect('light')
                    #__________________DARK THEME BUTTON PRESSED___________________________
                    if event.type == pygame.MOUSEBUTTONUP and optionsButtonHover == 1:
                        buttonSound.play()
                        themeSelect('dark')
                    #__________________BACK BUTTON PRESSED_______________________________
                    if event.type == pygame.MOUSEBUTTONUP and optionsButtonHover == 2:
                        buttonSound.play()
                        menu = 0
                        mainMenu()
        #___________________CHECKS IF INSTRUCTION MENU BUTTONS ARE ARE PRESSED___________________
        if menu == 5:
            for rect in instructionButtonPositions:
                if rect.collidepoint(pos):
                    instructionButtonHover = instructionButtonPositions.index(rect)
                    if event.type == pygame.MOUSEBUTTONUP and instructionButtonHover == 0:
                        buttonSound.play()
                        menu = 0
                        mainMenu()
                        return
                        
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONUP:
            if not playingAI:
                if menu == 1:
                    #__________________ CHECK IF USER PLACES A VERTICAL WALL_________________________
                    for rect in vertWallPositions:
                        if rect.collidepoint(pos):
                            index = vertWallPositions.index(rect)
                            row, col = index // 8, index % 8
                            placeWall(True, row, col)
                            return
                    #__________________ CHECK IF USER PLACES A HORIZONTAL WALL_________________________
                    for rect in horiWallPositions:
                        if rect.collidepoint(pos):
                            index = horiWallPositions.index(rect)
                            row, col = index // 9, index % 9
                            placeWall(False, row, col)
                            return
            else:
                if turn == 1: 
                    #__________________ CHECK IF USER PLACES A VERTICAL WALL (IN AI MODE)_________________________
                    for rect in vertWallPositions:
                        if rect.collidepoint(pos):
                            index = vertWallPositions.index(rect)
                            row, col = index // 8, index % 8
                            placeWall(True, row, col)
                            return
                    #__________________ CHECK IF USER PLACES A HORIZONTAL WALL (IN AI MODE_________________________
                    for rect in horiWallPositions:
                        if rect.collidepoint(pos):
                            index = horiWallPositions.index(rect)
                            row, col = index // 9, index % 9
                            placeWall(False, row, col)
                            return
                        
        #_____________________CHECKS IF USER MOVES A PIECE_____________________________________
        elif event.type == pygame.KEYDOWN:
            if not playingAI:
                if menu == 1:
                    if event.key == pygame.K_RIGHT:
                        if attemptMove('right'):
                            turn += 1
                    if event.key == pygame.K_LEFT:
                        if attemptMove('left'):
                            turn += 1
                    if event.key == pygame.K_UP:
                        if attemptMove('up'):
                            turn += 1
                    if event.key == pygame.K_DOWN:
                        if attemptMove('down'):
                            turn += 1
            #_____________________CHECKS IF USER MOVES A PIECE (AI MODE)_______________________________
            else:
                if turn == 1:
                    if menu == 1:
                        if event.key == pygame.K_RIGHT:
                            if attemptMove('right'):
                                turn += 1
                        if event.key == pygame.K_LEFT:
                            if attemptMove('left'):
                                turn += 1
                        if event.key == pygame.K_UP:
                            if attemptMove('up'):
                                turn += 1
                        if event.key == pygame.K_DOWN:
                            if attemptMove('down'):
                                turn += 1
            #______________CHECKS IF USER WANTS TO GO BACK TO MENU AFTER WIN____________________
            if event.key == pygame.K_ESCAPE:
                menu = 0
                mainMenu()

def updateScreen():

    #Updates the pygame display

    pygame.display.update()
    pygame.display.flip()

def setPieces():

    #Sets the player pieces onto the board in their correct spot depending on the number of players

    space_board[4][0] = 1
    space_board[4][8] = 2
    if numPlayers > 2:
        space_board[8][4] = 3
    if numPlayers > 3:
        space_board[0][4] = 4

def resetBoard():

    #Resets the board after a win (Resets wall counts, the turn, all boards, and wall positions)

    global space_board, vert_wall_board, hori_wall_board, wall_counts, turn, vertWallPositions, horiWallPositions, numPlayers
    space_board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    vert_wall_board = np.zeros((VERT_WALL_ROWS, VERT_WALL_COLS), dtype=int)
    hori_wall_board = np.zeros((HORI_WALL_ROWS, HORI_WALL_COLS), dtype=int)
    wall_counts = [10,10,10,10]
    turn = 1
    numPlayers = 2
    vertWallPositions = []
    horiWallPositions = []
    setPieces()

def attemptMove(direction):

    #Attempts to move the current player in the specified direction
    #Returns true if a succesful move is made or false if the move could not be made

    global space_board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if space_board[row][col] == turn:
                # ___________________ ATTEMPTS TO MAKE A MOVE RIGHT__________________
                if direction == 'right':
                    if col < 8 and vert_wall_board[row][col] == 0:
                        if space_board[row][col + 1] == 0:
                            pieceMoveSound.play()
                            space_board[row][col] = 0
                            space_board[row][col + 1] = turn
                            return True
                # ___________________ ATTEMPTS TO MAKE A MOVE LEFT__________________
                if direction == 'left':
                    if col > 0 and vert_wall_board[row][col - 1] == 0:
                        if space_board[row][col - 1] == 0:
                            pieceMoveSound.play()
                            space_board[row][col] = 0
                            space_board[row][col - 1] = turn
                            return True
                # ___________________ ATTEMPTS TO MAKE A MOVE UP__________________
                if direction == 'up':
                    if row > 0 and hori_wall_board[row - 1][col] == 0:
                        if space_board[row - 1][col] == 0:
                            pieceMoveSound.play()
                            space_board[row][col] = 0
                            space_board[row - 1][col] = turn
                            return True
                # ___________________ ATTEMPTS TO MAKE A MOVE DOWN__________________
                if direction == 'down':
                    if row < 8 and hori_wall_board[row][col] == 0:
                        if space_board[row + 1][col] == 0:
                            pieceMoveSound.play()
                            space_board[row][col] = 0
                            space_board[row + 1][col] = turn
                            return True
    return False

def transform_matrix(matrix):

    #Transforms the game matrix into a matrix that the pathfinding module can properly read
    #This makes 1s into 0s and 0s into 1s (Switches the values) to properly describe where walls are
    #Returns the new matrix

    rows = len(matrix)
    cols = len(matrix[0])
    for row in range(rows):
        for col in range(cols):
            if matrix[row][col] == 1:
                matrix[row][col] = 0
            elif matrix[row][col] == 0:
                matrix[row][col] = 1
            elif matrix[row][col] > 0:
                matrix[row][col] = 1
    return matrix

def findPath(matrix, startRow, startCol, endCords, computer):

    #Uses the pathfinding module to find the most optimal path between a piece and their goal
    #Returns an encoded list of coordinates

    possible_paths = []
    path = []
    for cord in endCords:
        endRow = cord[0]
        endCol = cord[1]
        grid = Grid(matrix=matrix)
        start = grid.node(startCol, startRow)
        end = grid.node(endCol, endRow)
        finder = AStarFinder()
        path, runs = finder.find_path(start, end, grid)
        if len(path) > 0:
            possible_paths.append(path)

    if len(possible_paths) > 0:
        min_length_sublist = min(possible_paths, key=len)
        if computer:
            return min_length_sublist, grid.grid_str(path=min_length_sublist)
        if not computer:
            return min_length_sublist
    else:
        return []

def getFullGameArray():

    #Combines all game arrays into one full game array for use in pathfinding (Wall array and Space array)
    #Returns the full game array

    new_array = []
    for row in range(9):
        odd_row_array = []
        even_row_array = []
        for col in range(9):
            if space_board[row][col] == 1:
                even_row_array.append(5)
            else:
                even_row_array.append(space_board[row][col])
            if col < 8:
                even_row_array.append(vert_wall_board[row][col])
            if row < 8:
                odd_row_array.append(hori_wall_board[row][col])
            if row < 8 and col < 8:
                odd_row_array.append(1)
        new_array.append(even_row_array)
        new_array.append(odd_row_array)
    new_array.pop()

    return new_array

def isPath(testRow, testCol, isVertical):

    #Figures out if a wall placement allows all players to have a path to a win
    #Returns True if all players can move with a potential wall placement or false otherwise.

    if isVertical:
        vert_wall_board[testRow][testCol] = 1
    if not isVertical:
        hori_wall_board[testRow][testCol] = 1
    
    #____________________COMBINES ALL MATRIXES FOR FIND PATH_________________
    new_array = getFullGameArray()
    test_array = copy.deepcopy(new_array)

    for startRow in range(0,len(new_array)):
        for startCol in range(0,len(new_array)):
            #_________________________________________CHECKS IF PLAYER 1 CAN MOVE WITH A POTENTIAL WALL PLACEMENT________________________________________
            if new_array[startRow][startCol] == 5:
                result1 = findPath(transform_matrix(test_array), startRow, startCol, [[16,16],[14,16],[12,16],[10,16],[8,16],[6,16],[4,16],[2,16],[0,16]], False)
                test_array = copy.deepcopy(new_array)
                steps_away = str(result1)
                if len(result1) < 1:
                    if isVertical:
                        vert_wall_board[testRow][testCol] = 0
                    if not isVertical:
                        hori_wall_board[testRow][testCol] = 0
                    new_array = []
                    print('PLAYER 1 CANT MOVE IF THAT WALL IS PLACED')
                    return False
            #_________________________________________CHECKS IF PLAYER 2 CAN MOVE WITH A POTENTIAL WALL PLACEMENT________________________________________
            if new_array[startRow][startCol] == 2:
                result2 = findPath(transform_matrix(test_array), startRow, startCol, [[16,0],[14,0],[12,0],[10,0],[8,0],[6,0],[4,0],[2,0],[0,0]], False)
                test_array = copy.deepcopy(new_array)
                steps_away = str(result2)
                if len(result2) < 1:
                    if isVertical:
                        vert_wall_board[testRow][testCol] = 0
                    if not isVertical:
                        hori_wall_board[testRow][testCol] = 0
                    new_array = []
                    print('PLAYER 2 CANT MOVE IF THAT WALL IS PLACED')
                    return False
            if numPlayers > 2:
            #_________________________________________CHECKS IF PLAYER 3 CAN MOVE WITH A POTENTIAL WALL PLACEMENT________________________________________
                if new_array[startRow][startCol] == 3:
                    result3 = findPath(transform_matrix(test_array), startRow, startCol, [[0,16],[0,14],[0,12],[0,10],[0,8],[0,16],[0,4],[0,2],[0,0]], False)
                    test_array = copy.deepcopy(new_array)
                    steps_away = str(result3)
                    if len(result3) < 1:
                        if isVertical:
                            vert_wall_board[testRow][testCol] = 0
                        if not isVertical:
                            hori_wall_board[testRow][testCol] = 0
                        new_array = []
                        print('PLAYER 3 CANT MOVE IF THAT WALL IS PLACED')
                        return False
            if numPlayers > 3:
                #_________________________________________CHECKS IF PLAYER 3 CAN MOVE WITH A POTENTIAL WALL PLACEMENT________________________________________
                if new_array[startRow][startCol] == 4:
                    result4 = findPath(transform_matrix(test_array), startRow, startCol, [[16,16],[16,14],[16,12],[16,10],[16,8],[16,16],[16,4],[16,2],[16,0]], False)
                    test_array = copy.deepcopy(new_array)
                    steps_away = str(result4)
                    if len(result4) < 1:
                        if isVertical:
                            vert_wall_board[testRow][testCol] = 0
                        if not isVertical:
                            hori_wall_board[testRow][testCol] = 0
                        new_array = []
                        print('PLAYER 4 CANT MOVE IF THAT WALL IS PLACED')
                        return False
    
    #REMEMBER TO REMOVE WALL AFTER TESTING
    new_array = []
    odd_row_array = []
    even_row_array = []
    if isVertical:
        vert_wall_board[testRow][testCol] = 0
    if not isVertical:
        hori_wall_board[testRow][testCol] = 0
    print('EVERYBODY CAN MOVE - ALLOWING WALL TO BE PLACED')
    return True

def extract_coordinates(result):

    #This function extracts the encoded coordinates from the findPath method to be used to find the computers best path to a win
    #returns a list of coordinates that can be used to move the computer piece

    coordinates = []
    for item in result:
        string = str(item)
        pattern = re.compile(r'GridNode\((\d+):(\d+)')
        match = pattern.search(string)
        if match:
            x = int(match.group(1))
            y = int(match.group(2))
            if x % 2 == 0 and y % 2 == 0:
                coordinates.append([int(y/2), int(x/2)])
    else:
        return coordinates

def computerTryMove():

    #Allows computer to move towards the shortest possible path to where they can win
    #Returns true if computer was able to make the move or false if their was an obstacle

    computer_array = getFullGameArray()
    test_array = copy.deepcopy(computer_array)
    for startRow in range(0,len(computer_array)):
            for startCol in range(0,len(computer_array)):
                if computer_array[startRow][startCol] == 2:
                    result, map = findPath(transform_matrix(test_array), startRow, startCol, [[16,0],[14,0],[12,0],[10,0],[8,0],[6,0],[4,0],[2,0],[0,0]], True)
                    test_array = copy.deepcopy(computer_array)        
                    coordinates = extract_coordinates(result)
                    print("_" * 50)
                    print("COMPUTER PATHFINDING")
                    print(map)  

                    if coordinates[0][0] < coordinates[1][0]:
                        if attemptMove('down'):
                            return True
                    if coordinates[0][0] > coordinates[1][0]:
                        if attemptMove('up'):
                            return True
                    if coordinates[0][1] > coordinates[1][1]:
                        if attemptMove('left'):
                            return True
                    if coordinates[0][1] < coordinates[1][1]:
                        if attemptMove('right'):
                            return True
                        
    return False

def computerTryWall():

    #Allows computer to place a wall in the path between the player and their desired path
    #Returns false if the computer can't place the desired wall or true if they did

    computer_array = getFullGameArray()
    test_array = copy.deepcopy(computer_array)
    for startRow in range(0,len(computer_array)):
            for startCol in range(0,len(computer_array)):
                if computer_array[startRow][startCol] == 5:
                    result, map = findPath(transform_matrix(test_array), startRow, startCol, [[16,16],[14,16],[12,16],[10,16],[8,16],[6,16],[4,16],[2,16],[0,16]], True)
                    test_array = copy.deepcopy(computer_array)        
                    coordinates = extract_coordinates(result)
                    print(coordinates)
                    #____CHECKS IF PLAYERS PATH IS GOING RIGHT AND PLACES A WALL IN THE WAY____________________
                    if coordinates[0][1] < coordinates[1][1]:
                        if placeWall(True, coordinates[0][0], coordinates[0][1]):
                            return True
                    #____CHECKS IF PLAYERS PATH IS GOING LEFT AND PLACES A WALL IN THE WAY____________________
                    #TODO TEST
                    if coordinates[0][1] > coordinates[1][1]:
                        if placeWall(True, coordinates[0][0], coordinates[0][1] - 1):
                            return True
                    #____CHECKS IF PLAYERS PATH IS GOING UP AND PLACES A WALL IN THE WAY____________________
                    #TODO TEST
                    if coordinates[0][0] > coordinates[1][0]:
                        if placeWall(False, coordinates[0][0] - 1, coordinates[0][1]):
                            return True
                    #____CHECKS IF PLAYERS PATH IS GOING DOWN AND PLACES A WALL IN THE WAY____________________
                    #TODO TEST
                    if coordinates[0][0] < coordinates[1][0]:
                        if placeWall(False, coordinates[0][0], coordinates[0][1]):
                            return True
                        
    return False

def computerMove():

    # Causes the AI to make a move (Either by moving a wall piece or by moving their character)
    # Returns true when the computer made a move

    #________________________GETS PLAYERS SHORTEST PATH TO WIN__________________________________
    computer_array = getFullGameArray()
    test_array = copy.deepcopy(computer_array)
    for startRow in range(0,len(computer_array)):
            for startCol in range(0,len(computer_array)):
                if computer_array[startRow][startCol] == 5:
                    result, map = findPath(transform_matrix(test_array), startRow, startCol, [[16,16],[14,16],[12,16],[10,16],[8,16],[6,16],[4,16],[2,16],[0,16]], True)
                    test_array = copy.deepcopy(computer_array)        
                    player_coordinates = extract_coordinates(result)

    #________________________GETS COMPUTERS SHORTEST PATH TO WIN__________________________________
    computer_array = getFullGameArray()
    test_array = copy.deepcopy(computer_array)
    for startRow in range(0,len(computer_array)):
            for startCol in range(0,len(computer_array)):
                if computer_array[startRow][startCol] == 2:
                    result, map = findPath(transform_matrix(test_array), startRow, startCol, [[16,0],[14,0],[12,0],[10,0],[8,0],[6,0],[4,0],[2,0],[0,0]], True)
                    test_array = copy.deepcopy(computer_array)        
                    computer_coordinates = extract_coordinates(result)

    #_______________COMPUTER ONLY PLACES A WALL IF PLAYER HAS A SHORTER PATH TO A WIN____________________
    if len(computer_coordinates) > len(player_coordinates):
         madeMove = computerTryWall()
    else:
         madeMove = computerTryMove()

    if not madeMove:
        madeMove = computerTryMove()

    #______________IF THE COMPUTER CAN"T PLACE A WALL IN ITS DESIRED PLACE OR MAKE A DESIRED MOVE IT MAKES A RANDOM MOVE_____________
    if not madeMove:
        choice = random.randint(0,4)
        if choice == 1:
            madeMove = attemptMove('down')
        if choice == 2:
            madeMove = attemptMove('up')
        if choice == 3:
            madeMove = attemptMove('left')
        if choice == 4:
            madeMove = attemptMove('right')
    #______________IF THE COMPUTER CAN"T MOVE IT PLACES A RANDOM WALL____________________
    if not madeMove:
        options = ['vertical','horizontal']
        selection = random.choice(options)
        if selection == 'vertical':
            print("VERTICAL")
            col = random.randint(0, VERT_WALL_COLS - 1)
            row = random.randint(0, VERT_WALL_ROWS - 1)
            print(row,col)
            if placeWall(True, row, col):
                madeMove = True
        if selection == 'horizontal':
            print("HORIZONTAL")
            col = random.randint(0, HORI_WALL_COLS - 1)
            row = random.randint(0, HORI_WALL_ROWS - 1)
            print(row,col)
            if placeWall(False, row, col):
                madeMove = True
    return True

def main():

    #Contains the main logic of the game and draws the game visuals

    global turn, menu
    setPieces()
    while True:
        if turn > numPlayers:
            turn = 1
        screen.fill(bg_color)
        createGameVisuals(turn)
        createHitboxes()
        if checkWin():
            menu = 2
        inputHandler()
        if not checkWin():
            if playingAI and turn == 2:
                if computerMove():
                    turn += 1
        updateScreen()

def mainMenu():

    #Handles the menus, only allows the current menu to be drawn on the screen

    global menuButtonPositions, optionsButtonPositions, selectPlayerButtonPositions, instructionButtonPositions
    while True:
        screen.fill(bg_color)
        if menu == 0: # Main Menu
            optionsButtonPositions = []
            createMenu()
        elif menu == 4: #Options Menu
            menuButtonPositions = []
            createOptionsMenu()
        elif menu == 3: #Select Player Menu
            selectPlayerButtonPositions = []
            screen.fill(bg_color)
            createPlayerSelectMenu()
        elif menu == 5: #Instructions Menu
            instructionButtonPositions = []
            createInstructionsMenu()
        inputHandler()
        updateScreen()

if __name__ == "__main__":
    mainMenu()