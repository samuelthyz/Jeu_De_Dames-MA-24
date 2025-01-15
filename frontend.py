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


def draw_sidebar(screen, black_name, gray_name,
                 black_time, gray_time, total_time,
                 black_pieces, gray_pieces,
                 black_caps, gray_caps,
                 draw_proposal):
    """
    Barre latérale : affiche infos sur les deux joueurs, stats de partie, proposition de nulle,
    et le message "Esc pour quitter" en rouge.
    """
    side_rect = pygame.Rect(BOARD_PIXEL_SIZE, 0, SIDEBAR_WIDTH, BOARD_PIXEL_SIZE)
    pygame.draw.rect(screen, PANEL_BG, side_rect)  # Fond de la sidebar
    pygame.draw.line(screen, PANEL_EDGE,
                     (BOARD_PIXEL_SIZE, 0),
                     (BOARD_PIXEL_SIZE, BOARD_PIXEL_SIZE), 3)  # Ligne de séparation

    x_side = BOARD_PIXEL_SIZE + 20  # Position x de départ pour le texte
    y_side = 20  # Position y de départ pour le texte

    # Affichage du nom et des infos du joueur Noir
    black_title = font_info.render(black_name, True, backend.PIECE_BLACK)
    screen.blit(black_title, (x_side, y_side))
    y_side += 40

    black_time_surf = font_info.render(f"Noir : {format_time(black_time)}", True, (211, 211, 211))
    screen.blit(black_time_surf, (x_side, y_side))
    y_side += 40

    black_rem_surf = font_info.render(f"Restants : {len(black_pieces)}", True, backend.PIECE_BLACK)
    screen.blit(black_rem_surf, (x_side, y_side))
    y_side += 40

    black_cap_surf = font_info.render(f"Captures : {black_caps}", True, backend.PIECE_BLACK)
    screen.blit(black_cap_surf, (x_side, y_side))
    y_side += 60

    # Statistiques globales
    moves_surf = font_info.render(f"Coups_total : {backend.game_stats['moves_count']}", True, (211, 211, 211))
    screen.blit(moves_surf, (x_side, y_side))
    y_side += 40

    totc_surf = font_info.render(f"Capt tot : {backend.game_stats['total_captures']}", True, (211, 211, 211))
    screen.blit(totc_surf, (x_side, y_side))
    y_side += 60

    total_surf = font_info.render(f"Durée : {format_time(total_time)}", True, (211, 211, 211))
    screen.blit(total_surf, (x_side, y_side))
    y_side += 80

    # Affichage des infos pour le joueur Gris
    gray_time_surf = font_info.render(f"Gris : {format_time(gray_time)}", True, (211, 211, 211))
    screen.blit(gray_time_surf, (x_side, y_side))
    y_side += 40

    gray_rem_surf = font_info.render(f"Restants : {len(gray_pieces)}", True, backend.PIECE_GRAY)
    screen.blit(gray_rem_surf, (x_side, y_side))
    y_side += 40

    gray_cap_surf = font_info.render(f"Captures : {gray_caps}", True, backend.PIECE_GRAY)
    screen.blit(gray_cap_surf, (x_side, y_side))
    y_side += 40

    gray_title = font_info.render(gray_name, True, backend.PIECE_GRAY)
    screen.blit(gray_title, (x_side, y_side))
    y_side += 60

    # Affiche la proposition de nulle, s'il y a lieu
    if draw_proposal:
        prop_surf = font_info.render(f"Nulle proposée : {draw_proposal}", True, (255, 0, 0))
        screen.blit(prop_surf, (x_side, y_side))
        y_side += 40

    # Message pour quitter le jeu avec la touche Esc en Rouge
    esc_msg = font_info.render("Esc pour quitter", True, (255, 0, 0))
    screen.blit(esc_msg, (x_side, y_side))


def cell_from_mouse(mx, my):
    """
    Convertit un clic (mx, my) en [row, col] sur le plateau.
    Retourne None si le clic est en dehors du plateau.
    """
    rx = mx - BOARD_MARGIN  # Position relative x par rapport au plateau
    ry = my - BOARD_MARGIN  # Position relative y par rapport au plateau
    if 0 <= rx < BOARD_SIZE * CELL_SIZE and 0 <= ry < BOARD_SIZE * CELL_SIZE:
        # Vérifie si le clic est à l'intérieur du damier
        row = ry // CELL_SIZE  # Calcule la ligne cliquée
        col = rx // CELL_SIZE  # Calcule la colonne cliquée
        return [row, col]  # Retourne la cellule en [row, col]
    return None  # En dehors du plateau, retourne None


def find_piece_at(cell, black_pieces, gray_pieces):
    """
    Vérifie si la case (row, col) contient un pion, noir ou gris.
    Retourne (arr, idx) si trouvé, sinon (None, None).
    """
    row, col = cell  # Décompose la cellule cliquée
    for i, p in enumerate(black_pieces):  # Cherche dans la liste des noirs
        if p[0] == row and p[1] == col:  # Si position correspondante
            return (black_pieces, i)  # Retourne la liste et l'indice
    for i, p in enumerate(gray_pieces):  # Cherche dans la liste des gris
        if p[0] == row and p[1] == col:
            return (gray_pieces, i)  # Retourne la liste et l'indice
    return (None, None)  # Pas de pièce trouvée


def fill_vertical_background(screen):
    """
    Applique le dégradé vertical de fond pour le menu.
    """
    fill_vertical_gradient(screen, MENU_COLOR_TOP, MENU_COLOR_BOTTOM)
    # Utilise la fonction de dégradé pour remplir l'écran
