"""
Nom : Backend.py
Auteurs : Dylan, Samuel
Date 11.11.2024
"""

###############################################################################
# Interface graphique du jeu de Dames 10x10.
#
# - Menus de début & fin avec dégradé
# - Polices agrandies
# - Mode Blitz (temps imposé, touche D pour nulle, S/L pour save/load)
# - Animation des déplacements (animate_move)
# - Sidebar affichant stats (nombre de coups, captures totales)
# - Couleur du pion noir plus visible : (10, 10, 10) géré dans backend
###############################################################################

import pygame  # Import de Pygame pour toute la partie graphique
import backend  # Import du backend pour les fonctions de logique du jeu

# Paramètres du damier
BOARD_SIZE = 10  # Taille du plateau en cases (10x10)
CELL_SIZE = 80  # Dimension de chaque case en pixels
BOARD_MARGIN = 20  # Marge autour du plateau
SIDEBAR_WIDTH = 300  # Largeur de la barre latérale d'affichage des stats
BOARD_PIXEL_SIZE = BOARD_SIZE * CELL_SIZE + BOARD_MARGIN * 2  # Taille totale du plateau en pixels

# Couleurs interface
MENU_COLOR_TOP = (60, 110, 130)  # Couleur haut du dégradé du menu
MENU_COLOR_BOTTOM = (180, 210, 220)  # Couleur bas du dégradé du menu
PANEL_BG = (245, 245, 245)  # Couleur de fond pour le panneau latéral
PANEL_EDGE = (120, 120, 120)  # Couleur du contour du panneau latéral
TEXT_COLOR = (30, 30, 30)  # Couleur de texte par défaut
BOARD_BLACK = (50, 50, 50)  # Couleur des cases noires du damier
BOARD_WHITE = (240, 240, 240)  # Couleur des cases blanches du damier
BOARD_FRAME = (80, 80, 80)  # Couleur du cadre entourant le damier
PIECE_HALO = (255, 0, 0)  # Couleur pour surligner une pièce sélectionnée (halo rouge)

# Mode Blitz
BLITZ_MODE = True  # Active le mode Blitz si True
BLITZ_TIME_LIMIT = 120  # Limite de temps en secondes pour le mode Blitz

font_title = None  # Police pour les titres, initialisée plus tard
font_menu = None  # Police pour les menus
font_info = None  # Police pour les informations affichées


def init_fonts():
    """
    Initialise les polices pour l'affichage.
    """
    global font_title, font_menu, font_info  # On déclare globales pour pouvoir modifier ces variables
    pygame.font.init()  # Initialise le module de font de Pygame
    font_title = pygame.font.SysFont("Arial", 56, bold=True)  # Police pour les titres en Arial taille 56, en gras
    font_menu = pygame.font.SysFont("Arial", 40, bold=True)  # Police pour les menus en Arial taille 40, en gras
    font_info = pygame.font.SysFont("Arial", 32, bold=True)  # Police pour les infos en Arial taille 32, en gras


def format_time(seconds):
    """
    Convertit un temps en secondes en mm:ss.
    """
    m, s = divmod(int(seconds), 60)  # Divise pour obtenir minutes et secondes
    return f"{m:02d}:{s:02d}"  # Format string pour afficher avec deux chiffres


def fill_vertical_gradient(surface, top, bottom):
    """
    Applique un dégradé vertical (du haut en bas) sur toute la surface.
    """
    width, height = surface.get_size()  # Récupère la taille de la surface
    for y in range(height):  # Parcourt chaque ligne verticale
        ratio = y / float(height)  # Calcule le ratio de progression
        color = (  # Calcule la couleur interpolée pour cette ligne
            int(top[0] + (bottom[0] - top[0]) * ratio),
            int(top[1] + (bottom[1] - top[1]) * ratio),
            int(top[2] + (bottom[2] - top[2]) * ratio)
        )
        pygame.draw.line(surface, color, (0, y), (width, y))
        # Dessine une ligne horizontale avec la couleur calculée


def draw_board(screen):
    """
    Dessine le damier 10x10 et son cadre.
    """
    pygame.draw.rect(screen, BOARD_FRAME,
                     (BOARD_MARGIN - 10, BOARD_MARGIN - 10,
                      BOARD_SIZE * CELL_SIZE + 20,
                      BOARD_SIZE * CELL_SIZE + 20))
    # Dessine le cadre autour du damier
    for row in range(BOARD_SIZE):  # Parcourt chaque ligne
        for col in range(BOARD_SIZE):  # Parcourt chaque colonne
            color = BOARD_BLACK if ((row + col) % 2 == 0) else BOARD_WHITE
            # Alterne la couleur de la case en fonction des indices
            x = col * CELL_SIZE + BOARD_MARGIN  # Calcule la position x sur l'écran
            y = row * CELL_SIZE + BOARD_MARGIN  # Calcule la position y sur l'écran
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            # Dessine la case


def draw_pawn(screen, piece, color):
    """
    Dessine un pion (ou dame).
    piece = [row, col, isQueen]
    color = backend.PIECE_BLACK ou backend.PIECE_GRAY
    """
    row, col, isQ = piece  # Décompose la pièce (ligne, colonne, dame ou pas)
    cx = col * CELL_SIZE + CELL_SIZE // 2 + BOARD_MARGIN
    # Coordonnée x du centre de la case
    cy = row * CELL_SIZE + CELL_SIZE // 2 + BOARD_MARGIN
    # Coordonnée y du centre de la case
    r = CELL_SIZE // 3  # Rayon pour dessiner le pion
    pygame.draw.circle(screen, color, (cx, cy), r)
    # Dessine le cercle représentant le pion
    if isQ:  # Si la pièce est une dame
        pygame.draw.circle(screen, backend.PIECE_QUEEN, (cx, cy), r // 2)
        # Dessine un cercle plus petit au centre pour symboliser la dame


def highlight_pawn(screen, selected):
    """
    Surligne la pièce sélectionnée : (arr, idx).
    """
    if selected:  # Si une pièce est sélectionnée
        arr, idx = selected  # Récupère l'array et l'indice de la pièce
        row, col, _ = arr[idx]  # Récupère la position de la pièce
        cx = col * CELL_SIZE + CELL_SIZE // 2 + BOARD_MARGIN
        # Calcule la coordonnée x du centre de la case
        cy = row * CELL_SIZE + CELL_SIZE // 2 + BOARD_MARGIN
        # Calcule la coordonnée y du centre de la case
        r = CELL_SIZE // 3  # Rayon utilisé pour le pion
        pygame.draw.circle(screen, PIECE_HALO, (cx, cy), r + 8, 4)
        # Dessine le halo autour de la pièce


def animate_move(screen, piece, start_pos, end_pos, steps=10):
    """
    Anime le déplacement (start_pos -> end_pos) en 'steps' étapes.
    Réduction latence : time.wait(10) au lieu de 20.
    """
    (sr, sc) = start_pos  # Position de départ (ligne, colonne)
    (er, ec) = end_pos  # Position finale (ligne, colonne)
    row_delta = (er - sr) / steps  # Variation par étape en ligne
    col_delta = (ec - sc) / steps  # Variation par étape en colonne
    original_state = piece[:]  # Sauvegarde de l'état original de la pièce

    for i in range(steps + 1):  # Boucle pour animer le mouvement
        piece[0] = sr + row_delta * i  # Calcule la nouvelle ligne
        piece[1] = sc + col_delta * i  # Calcule la nouvelle colonne
        pygame.display.flip()  # Actualise l'affichage
        pygame.time.wait(10)  # Attend 10ms pour une animation plus fluide

    # On place définitivement la pièce à sa position finale
    piece[0], piece[1], piece[2] = er, ec, original_state[2]
