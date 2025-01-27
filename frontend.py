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
import sys  # Import de sys, pour pouvoir quitter le programme proprement
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


def draw_label(screen, label="Dylan, Samuel"):
    """
    Affiche un label discret en bas à gauche de l'écran.
    """
    font = pygame.font.SysFont("Arial", 20)  # Police discrète
    label_surface = font.render(label, True, (128, 128, 128))  # Texte gris discret
    screen.blit(label_surface, (10, screen.get_height() - 30))  # Bas à gauche avec un petit padding


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
    Le damier est centré avec des marges visibles autour.
    """
    # Calcul de la position et dimensions du cadre
    frame_x = BOARD_MARGIN - 10
    frame_y = BOARD_MARGIN - 10
    frame_width = BOARD_SIZE * CELL_SIZE + 20
    frame_height = BOARD_SIZE * CELL_SIZE + 20

    # Dessine le cadre du damier
    pygame.draw.rect(screen, BOARD_FRAME, (frame_x, frame_y, frame_width, frame_height))

    # Dessine les cases du damier
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # Alterne la couleur de la case en fonction des indices
            color = BOARD_BLACK if ((row + col) % 2 == 0) else BOARD_WHITE

            # Calcul des coordonnées de la case
            x = col * CELL_SIZE + BOARD_MARGIN
            y = row * CELL_SIZE + BOARD_MARGIN

            # Dessine la case
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))


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

    x_side = BOARD_PIXEL_SIZE + 60  # Position x de départ pour le texte
    y_side = 60  # Position y de départ pour le texte

    y_black_start = BOARD_PIXEL_SIZE // 7  # Position verticale de départ
    x_center = BOARD_PIXEL_SIZE + SIDEBAR_WIDTH // 2  # Centre horizontal de la sidebar

    # Nom du joueur Noir
    black_title = font_info.render(black_name, True, backend.PIECE_BLACK)
    black_title_width = black_title.get_width()
    screen.blit(black_title, (x_center - black_title_width // 2, y_black_start))
    y_black_start += 40

    # Temps restant pour Noir
    black_time_surf = font_info.render(f"Noir : {format_time(black_time)}", True, (0, 0, 0))
    black_time_width = black_time_surf.get_width()
    screen.blit(black_time_surf, (x_center - black_time_width // 2, y_black_start))
    y_black_start += 40

    # Pions restants pour Noir
    black_rem_surf = font_info.render(f"Restants : {len(black_pieces)}", True, backend.PIECE_BLACK)
    black_rem_width = black_rem_surf.get_width()
    screen.blit(black_rem_surf, (x_center - black_rem_width // 2, y_black_start))
    y_black_start += 40

    # Captures réalisées par Noir
    black_cap_surf = font_info.render(f"Captures : {black_caps}", True, backend.PIECE_BLACK)
    black_cap_width = black_cap_surf.get_width()
    screen.blit(black_cap_surf, (x_center - black_cap_width // 2, y_black_start))
    y_black_start += 60

    y_stats_start = BOARD_PIXEL_SIZE // 3  # Position verticale de départ
    x_center = BOARD_PIXEL_SIZE + SIDEBAR_WIDTH // 2  # Centre horizontal de la sidebar

    # Statistique : Coups total
    moves_surf = font_info.render(f"Coups_total : {backend.game_stats['moves_count']}", True, (10, 50, 180))
    moves_width = moves_surf.get_width()  # Largeur du texte pour le centrer
    screen.blit(moves_surf, (x_center - moves_width // 2, y_stats_start))
    y_stats_start += 40

    # Statistique : Captures totales
    totc_surf = font_info.render(f"Capt tot : {backend.game_stats['total_captures']}", True, (10, 50, 180))
    totc_width = totc_surf.get_width()
    screen.blit(totc_surf, (x_center - totc_width // 2, y_stats_start))
    y_stats_start += 60

    # Statistique : Durée
    total_surf = font_info.render(f"Durée : {format_time(total_time)}", True, (10, 50, 180))
    total_width = total_surf.get_width()
    screen.blit(total_surf, (x_center - total_width // 2, y_stats_start))
    y_stats_start += 80

    y_gray_start = BOARD_PIXEL_SIZE // 2  # Position verticale (au milieu de la sidebar)
    x_center = BOARD_PIXEL_SIZE + SIDEBAR_WIDTH // 2  # Centre horizontal de la sidebar

    gray_time_surf = font_info.render(f"Gris : {format_time(gray_time)}", True, (128, 128, 128))
    gray_time_width = gray_time_surf.get_width()  # Largeur du texte
    screen.blit(gray_time_surf, (x_center - gray_time_width // 2, y_gray_start))
    y_gray_start += 40

    gray_rem_surf = font_info.render(f"Restants : {len(gray_pieces)}", True, (128, 128, 128))
    gray_rem_width = gray_rem_surf.get_width()
    screen.blit(gray_rem_surf, (x_center - gray_rem_width // 2, y_gray_start))
    y_gray_start += 40

    gray_cap_surf = font_info.render(f"Captures : {gray_caps}", True, (128, 128, 128))
    gray_cap_width = gray_cap_surf.get_width()
    screen.blit(gray_cap_surf, (x_center - gray_cap_width // 2, y_gray_start))
    y_gray_start += 40

    gray_title = font_info.render(gray_name, True, (128, 128, 128))
    gray_title_width = gray_title.get_width()
    screen.blit(gray_title, (x_center - gray_title_width // 2, y_gray_start))
    y_gray_start += 60

    # Affiche la proposition de nulle, s'il y a lieu
    if draw_proposal:
        prop_surf = font_info.render(f"Nulle proposée : {draw_proposal}", True, (255, 0, 0))
        screen.blit(prop_surf, (x_side, y_side))
        y_side += 40

    # Calcul de la position pour toujours afficher en bas
    esc_msg = font_info.render("Esc pour quitter la partie", True, (255, 0, 0))  # Message pour quitter la partie
    esc_msg_width = esc_msg.get_width()
    x_esc = BOARD_PIXEL_SIZE + (SIDEBAR_WIDTH - esc_msg_width) // 2  # Centrage horizontal
    y_esc = BOARD_PIXEL_SIZE - 100  # 100 pixels au-dessus du bas de la sidebar
    screen.blit(esc_msg, (x_esc, y_esc))


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


def show_start_menu(screen):
    """
    Affiche le menu de début et retourne True pour lancer la partie, False pour quitter.
    """
    selected_option = 0  # Option sélectionnée initialement
    item_font = pygame.font.SysFont("Arial", 40, bold=True)
    options = ["Lancer la partie", "Quitter"]  # Options du menu
    running = True  # Boucle de menu active

    while running:
        fill_vertical_background(screen)  # Remplit le fond avec le dégradé
        panel_w, panel_h = 600, 300  # Dimensions du panneau de menu
        px = (screen.get_width() - panel_w) // 2  # Calcule la position x du panneau
        py = (screen.get_height() - panel_h) // 2  # Calcule la position y du panneau

        pygame.draw.rect(screen, PANEL_BG, (px, py, panel_w, panel_h), border_radius=20)
        pygame.draw.rect(screen, PANEL_EDGE, (px, py, panel_w, panel_h), width=4, border_radius=20)

        title_surf = font_title.render("Menu Principal", True, TEXT_COLOR)
        screen.blit(title_surf, (px + (panel_w - title_surf.get_width()) // 2, py + 40))

        startY = py + 120  # Position de départ verticale pour les options
        for i, opt in enumerate(options):
            c = (255, 0, 0) if i == selected_option else TEXT_COLOR
            surf = item_font.render(opt, True, c)
            screen.blit(surf, (px + (panel_w - surf.get_width()) // 2, startY + i * 60))

        # Ajout du label discret en bas à gauche
        draw_label(screen)

        pygame.display.flip()  # Actualise l'affichage
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False  # Quitte si la fenêtre est fermée
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif ev.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif ev.key == pygame.K_RETURN:
                    return (selected_option == 0)  # Retourne True si "Lancer la partie" est choisi


def get_player_names(screen):
    """
    Permet la saisie du nom des joueurs (Noir puis Gris) avec un dégradé bleu.
    """
    # Initialisation de la police pour le texte de saisie
    input_font = pygame.font.SysFont("Arial", 40, bold=True)

    # Variables pour stocker les noms des joueurs
    black_name = ""  # Nom du joueur Noir
    gray_name = ""  # Nom du joueur Gris
    field = "black"  # Champ actuellement actif, commence par les pions noirs

    running = True  # Contrôle de la boucle de saisie

    while running:
        # Dessine un dégradé bleu en arrière-plan
        fill_vertical_background(screen)

        # Détermine le texte du prompt selon le champ actif (Noir ou Gris)
        prompt_txt = "Nom (pions noirs) :" if field == "black" else "Nom (pions gris) :"
        prompt_surf = input_font.render(prompt_txt, True, TEXT_COLOR)

        # Affiche le texte du prompt au centre horizontalement, à 1/3 de la hauteur
        screen.blit(prompt_surf, (screen.get_width() // 2 - prompt_surf.get_width() // 2,
                                  screen.get_height() // 3 - prompt_surf.get_height()))

        # Texte actuellement saisi (Noir ou Gris)
        current_txt = black_name if field == "black" else gray_name
        text_surf = input_font.render(current_txt, True, (0, 0, 0))  # Texte en noir

        # Affiche le texte saisi au centre horizontalement, au milieu de l'écran
        screen.blit(text_surf, (screen.get_width() // 2 - text_surf.get_width() // 2,
                                screen.get_height() // 2))

        # Ajoute le label "Dylan, Samuel" discrètement en bas à gauche
        draw_label(screen)

        # Rafraîchit l'affichage
        pygame.display.flip()

        # Gère les événements clavier et de fenêtre
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:  # Si l'utilisateur ferme la fenêtre
                pygame.quit()
                sys.exit()  # Quitte le programme
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:  # Si l'utilisateur appuie sur "Entrée"
                    if current_txt.strip():  # Vérifie que du texte a été saisi
                        if field == "black":  # Si c'était le champ Noir, passe au champ Gris
                            field = "gray"
                        else:  # Sinon, les deux noms ont été saisis, retourne les résultats
                            return black_name.strip(), gray_name.strip()
                elif ev.key == pygame.K_BACKSPACE:  # Supprime le dernier caractère
                    if field == "black":
                        black_name = black_name[:-1]
                    else:
                        gray_name = gray_name[:-1]
                else:  # Ajoute les caractères imprimables au texte en cours
                    ch = ev.unicode
                    if ch.isprintable():  # Vérifie que le caractère est imprimable
                        if field == "black":
                            black_name += ch
                        else:
                            gray_name += ch


def show_end_menu(screen,
                  black_name, gray_name,
                  black_time, gray_time, total_time,
                  black_pieces, gray_pieces,
                  black_captures, gray_captures):
    """
    Affiche le menu de fin avec un résumé de la partie.
    """
    end_font = pygame.font.SysFont("Arial", 50, bold=True)
    info_font = pygame.font.SysFont("Arial", 40)
    panel_w, panel_h = 1000, 600  # Dimensions du panneau de fin
    px = (screen.get_width() - panel_w) // 2  # Position x pour centrer le panneau
    py = (screen.get_height() - panel_h) // 2  # Position y pour centrer le panneau
    margin_x = 40  # Marge horizontale pour éviter que les textes soient trop proches des bords

    # Dégradé bleu pour le fond
    MENU_COLOR_TOP = (60, 110, 130)  # Couleur haut du dégradé
    MENU_COLOR_BOTTOM = (180, 210, 220)  # Couleur bas du dégradé
    fill_vertical_gradient(screen, MENU_COLOR_TOP, MENU_COLOR_BOTTOM)  # Applique le dégradé

    # Dessine le panneau central
    pygame.draw.rect(screen, (240, 240, 240), (px, py, panel_w, panel_h), border_radius=15)
    pygame.draw.rect(screen, (100, 100, 150), (px, py, panel_w, panel_h), width=4, border_radius=15)

    # Titre du menu
    title_surf = end_font.render("Résumé de la partie", True, (0, 0, 0))
    screen.blit(title_surf, (px + (panel_w - title_surf.get_width()) // 2, py + 30))

    # Contenu du menu
    black_rem = len(black_pieces)
    gray_rem = len(gray_pieces)

    lines = [
        f"Temps total : {format_time(total_time)}",
        f"{black_name} - Temps : {format_time(black_time)} | Captures : {black_captures} | Restants : {black_rem}",
        f"{gray_name} - Temps : {format_time(gray_time)} | Captures : {gray_captures} | Restants : {gray_rem}",
        f"Coups joués : {backend.game_stats['moves_count']}",
        f"Captures totales : {backend.game_stats['total_captures']}"
    ]

    # Calculer la hauteur totale occupée par les lignes
    line_spacing = 50  # Espacement entre chaque ligne
    total_height = len(lines) * line_spacing  # Hauteur totale de toutes les lignes

    # Calculer le point de départ pour centrer verticalement
    y_start = py + (panel_h - total_height) // 2

    # Centrage horizontal et affichage des lignes
    for line in lines:
        txt = info_font.render(line, True, (0, 0, 0))
        x_centered = px + (panel_w - txt.get_width()) // 2  # Centre horizontalement
        screen.blit(txt, (x_centered, y_start))
        y_start += line_spacing

    # Bouton "Esc pour quitter"
    esc_msg = info_font.render(" Veuillez cliquer Esc pour quitter", True, (255, 0, 0))  # Message en rouge
    esc_msg_width = esc_msg.get_width()
    x_esc = px + (panel_w - esc_msg_width) // 2  # Centre horizontalement
    y_esc = py + panel_h - 60  # Place en bas du panneau récapitulatif
    screen.blit(esc_msg, (x_esc, y_esc))  # Affiche le message

    draw_label(screen)
    pygame.display.flip()

    pygame.display.flip()  # Met à jour l'affichage
    waiting = True
    while waiting:  # Boucle d'attente
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:  # Si l'utilisateur ferme la fenêtre
                waiting = False  # Quitte la boucle
            elif ev.type == pygame.KEYDOWN:  # Si une touche est pressée
                if ev.key == pygame.K_ESCAPE:  # Vérifie si c'est "Esc"
                    waiting = False  # Quitte le menu récapitulatif


def show_popup(screen, message):
    """
    Affiche une pop-up au centre de l'écran avec un message en rouge.
    """
    # Taille et position de la pop-up
    popup_width, popup_height = 500, 250
    popup_x = (screen.get_width() - popup_width) // 2
    popup_y = (screen.get_height() - popup_height) // 2

    # Couleurs
    popup_background = (240, 240, 240)  # Fond clair
    popup_border = (0, 0, 0)  # Bordure noire
    text_color = (255, 0, 0)  # Texte en rouge
    button_color = (0, 120, 215)  # Bouton bleu
    button_text_color = (255, 255, 255)  # Texte du bouton blanc

    # Dessine la pop-up avec une bordure
    pygame.draw.rect(screen, popup_background, (popup_x, popup_y, popup_width, popup_height), border_radius=10)
    pygame.draw.rect(screen, popup_border, (popup_x, popup_y, popup_width, popup_height), width=4, border_radius=10)

    # Affiche le message en rouge, centré dans la pop-up
    font = pygame.font.SysFont("Arial", 40, bold=True)
    text_surface = font.render(message, True, text_color)
    text_x = popup_x + (popup_width - text_surface.get_width()) // 2
    text_y = popup_y + (popup_height - text_surface.get_height()) // 2 - 20  # Ajustement vertical
    screen.blit(text_surface, (text_x, text_y))

    # Ajoute un bouton "OK" au bas de la pop-up
    button_font = pygame.font.SysFont("Arial", 30)
    button_surface = button_font.render("OK", True, button_text_color)
    button_width, button_height = 120, 50
    button_x = popup_x + (popup_width - button_width) // 2
    button_y = popup_y + popup_height - 80
    pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height), border_radius=8)
    screen.blit(button_surface, (button_x + (button_width - button_surface.get_width()) // 2,
                                 button_y + (button_height - button_surface.get_height()) // 2))

    pygame.display.flip()

    # Attend que l'utilisateur clique sur "OK" pour fermer la pop-up
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if button_x <= mx <= button_x + button_width and button_y <= my <= button_y + button_height:
                    waiting = False  # Ferme la pop-up


def run_game():
    """
    Boucle principale du jeu.
    - Récupère la résolution de l'écran pour s'adapter en plein écran.
    - Initialise dynamiquement les dimensions du plateau et de la sidebar.
    - Gère le reste du jeu (menus, animations, etc.) et permet de quitter avec Esc.
    """
    pygame.init()  # Initialise tous les modules Pygame
    init_fonts()  # Initialise les polices utilisées dans le jeu

    # Récupération de la résolution de l'écran
    infoObject = pygame.display.Info()  # Récupère les informations sur l'affichage courant
    screen_w = infoObject.current_w  # Largeur actuelle de l'écran
    screen_h = infoObject.current_h  # Hauteur actuelle de l'écran

    # Définition d'un ratio pour le plateau et la sidebar (70% pour le plateau, 30% pour la sidebar)
    board_width = int(screen_w * 0.7)  # Le plateau occupe 70% de la largeur
    sidebar_width = screen_w - board_width  # La sidebar occupe le reste

    # Pour avoir un plateau carré, on prend la dimension minimale entre board_width et screen_h
    board_size_pixels = min(board_width, screen_h)  # Taille maximale du plateau carré

    # Détermination de la taille du plateau, du CELL_SIZE, de la marge, etc.
    global CELL_SIZE, BOARD_MARGIN, SIDEBAR_WIDTH, BOARD_PIXEL_SIZE
    BOARD_SIZE = 10  # Le plateau est de 10x10 cases
    CELL_SIZE = board_size_pixels // BOARD_SIZE  # Taille d'une case
    BOARD_MARGIN = CELL_SIZE // 8  # Marge autour du plateau (ici 1/8 de CELL_SIZE)
    BOARD_PIXEL_SIZE = BOARD_SIZE * CELL_SIZE + BOARD_MARGIN * 2  # Taille totale du plateau
    SIDEBAR_WIDTH = sidebar_width  # Largeur de la sidebar selon la résolution

    # Création de la fenêtre en plein écran
    screen = pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN)
    pygame.display.set_caption("Dames 10x10 - Adaptatif")

    if not show_start_menu(screen):  # Affiche le menu de démarrage et quitte si l'utilisateur choisit "Quitter"
        return

    black_name, gray_name = get_player_names(screen)  # Saisie des noms des joueurs
    backend.reset_game_state()  # Réinitialise l'état du jeu dans le backend

    # Placement initial des pions sur le plateau.
    # Les pions noirs sur les 4 premières lignes et gris sur les 4 dernières (cases alternées)
    black_pieces = [[r, c, False] for r in range(4) for c in range(BOARD_SIZE) if (r + c) % 2 == 0]
    gray_pieces = [[r, c, False] for r in range(6, 10) for c in range(BOARD_SIZE) if (r + c) % 2 == 0]

    black_turn = True  # Le tour commence avec le joueur Noir
    black_caps = 0  # Compteur de captures pour Noir initialisé à zéro
    gray_caps = 0  # Compteur de captures pour Gris initialisé à zéro
    total_time = 0.0  # Temps total de la partie
    BLITZ_MODE = True  # Active le mode Blitz
    BLITZ_TIME_LIMIT = 120  # Limite de temps (en secondes) pour chaque joueur en mode Blitz
    black_time = BLITZ_TIME_LIMIT if BLITZ_MODE else 0.0  # Temps restant pour Noir
    gray_time = BLITZ_TIME_LIMIT if BLITZ_MODE else 0.0  # Temps restant pour Gris
    last_tick = pygame.time.get_ticks()  # Stocke le temps de départ en millisecondes

    backend.update_position_history(black_pieces, gray_pieces, black_turn)  # Met à jour l'historique des positions

    continuingCap = False  # Indique si une capture en chaîne est en cours
    capturingPiece = None  # La pièce qui effectue une capture en chaîne
    selectedPawn = None  # La pièce sélectionnée par le joueur
    possibleMoves = []  # Liste des coups possibles pour la pièce sélectionnée
    drawProposal = None  # Proposition de nulle si les joueurs s'accordent
    running = True  # Condition pour maintenir la boucle principale du jeu
    clock = pygame.time.Clock()  # Horloge pour gérer le taux d'images (FPS)

    while running:  # Boucle principale du jeu
        clock.tick(60)  # Limite la boucle à 60 FPS
        now = pygame.time.get_ticks()  # Temps actuel en millisecondes
        dt = (now - last_tick) / 1000.0  # Temps écoulé depuis la dernière itération (en secondes)
        total_time += dt  # Incrémente le temps total de jeu
        # Gestion du mode Blitz (décompte du temps du joueur actif)
        if BLITZ_MODE:
            if black_turn:  # Si c'est le tour des noirs
                black_time -= dt  # Décrémente le temps restant pour noir
                if black_time <= 0:  # Si le temps est épuisé pour noir
                    black_time = 0  # On fixe le temps à 0
                    screen.fill((0, 0, 0))  # Remplit l'écran de noir
                    msg = font_title.render("Temps épuisé (Noir) -> Gris gagne", True, (255, 0, 0))
                    screen.blit(msg, (screen_w // 2 - msg.get_width() // 2,
                                      screen_h // 2 - msg.get_height() // 2))
                    pygame.display.flip()  # Actualise l'affichage
                    pygame.time.wait(3000)  # Attend 3 secondes
                    running = False  # Termine la boucle du jeu
                    break
            else:  # Sinon, c'est le tour des gris
                gray_time -= dt  # Décrémente le temps restant pour gris
                if gray_time <= 0:  # Si le temps est épuisé pour gris
                    gray_time = 0  # Fixe le temps à 0
                    screen.fill((0, 0, 0))  # Remplit l'écran de noir
                    msg = font_title.render("Temps épuisé (Gris) -> Noir gagne", True, (255, 0, 0))
                    screen.blit(msg, (screen_w // 2 - msg.get_width() // 2,
                                      screen_h // 2 - msg.get_height() // 2))
                    pygame.display.flip()  # Actualise l'affichage
                    pygame.time.wait(3000)  # Attend 3 secondes
                    running = False  # Termine la boucle du jeu
                    break
        else:
            # En mode normal, on incrémente le temps du joueur actif (sans décompte)
            if black_turn:
                black_time += dt
            else:
                gray_time += dt

        last_tick = now  # Met à jour le temps de référence

        # Vérification si un joueur a gagné
        endVal = backend.check_winner(black_pieces, gray_pieces)
        if endVal:
            screen.fill((220, 220, 220))  # Remplit l'écran d'une couleur claire
            draw_board(screen)  # Redessine le plateau
            for b_p in black_pieces:  # Redessine les pions noirs
                draw_pawn(screen, b_p, backend.PIECE_BLACK)
            for g_p in gray_pieces:  # Redessine les pions gris
                draw_pawn(screen, g_p, backend.PIECE_GRAY)
            # Vérification si un joueur a gagné
            endVal = backend.check_winner(black_pieces, gray_pieces)
            if endVal:
                show_popup(screen, f"{endVal} a gagné !")
                running = False
                break

        # Vérification de la règle des 50 coups sans capture
        if backend.no_capture_turns >= 50:
            screen.fill((220, 220, 220))
            draw_board(screen)
            for b_p in black_pieces:
                draw_pawn(screen, b_p, backend.PIECE_BLACK)
            for g_p in gray_pieces:
                draw_pawn(screen, g_p, backend.PIECE_GRAY)
            msg = font_menu.render("Nul (50 coups)", True, (255, 0, 0))
            screen.blit(msg, (screen_w // 2 - msg.get_width() // 2,
                              screen_h // 2 - msg.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False
            break

        # Vérification de la règle de répétition des positions (nul par répétition)
        if backend.is_repeated_position(black_pieces, gray_pieces, black_turn):
            screen.fill((220, 220, 220))
            draw_board(screen)
            for b_p in black_pieces:
                draw_pawn(screen, b_p, backend.PIECE_BLACK)
            for g_p in gray_pieces:
                draw_pawn(screen, g_p, backend.PIECE_GRAY)
            msg = font_menu.render("Nul (répétition)", True, (255, 0, 0))
            screen.blit(msg, (screen_w // 2 - msg.get_width() // 2,
                              screen_h // 2 - msg.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False
            break

        # Détermine la couleur du joueur actif
        colorNow = backend.PIECE_BLACK if black_turn else backend.PIECE_GRAY

        # Si aucune capture en chaîne n'est en cours, on récupère tous les coups possibles pour le joueur actif
        if not continuingCap:
            movesAll = backend.find_all_possible_moves(colorNow, black_pieces, gray_pieces)
            if not movesAll:
                screen.fill((220, 220, 220))
                draw_board(screen)
                for b_p in black_pieces:
                    draw_pawn(screen, b_p, backend.PIECE_BLACK)
                for g_p in gray_pieces:
                    draw_pawn(screen, g_p, backend.PIECE_GRAY)
                whoWin = "NOIR" if colorNow == backend.PIECE_GRAY else "GRIS"
                msg = font_title.render(f"{whoWin} gagne (blocage) !", True, (255, 0, 0))
                screen.blit(msg, (screen_w // 2 - msg.get_width() // 2,
                                  screen_h // 2 - msg.get_height() // 2))
                pygame.display.flip()
                pygame.time.wait(2000)
                running = False
                break

        # Redessine l'écran : fond, plateau et les pions
        screen.fill((220, 220, 220))
        draw_board(screen)
        for bpiece in black_pieces:
            draw_pawn(screen, bpiece, backend.PIECE_BLACK)
        for gpiece in gray_pieces:
            draw_pawn(screen, gpiece, backend.PIECE_GRAY)
        highlight_pawn(screen, selectedPawn)

        # Affiche la sidebar avec les informations et le message "Esc pour quitter"
        draw_sidebar(screen, black_name, gray_name,
                     black_time, gray_time, total_time,
                     black_pieces, gray_pieces,
                     black_caps, gray_caps,
                     drawProposal)

        pygame.display.flip()  # Met à jour l'affichage de la fenêtre

        # Gestion des coups obligatoires
        if not continuingCap:
            capturesNow = [m for m in backend.find_all_possible_moves(colorNow, black_pieces, gray_pieces)
                           if m['type'] == 'capture']
            mustCapture = bool(capturesNow)
        else:
            mustCapture = True

        # Gestion des événements (clavier, souris, etc.)
        evs = pygame.event.get()
        for ev in evs:
            if ev.type == pygame.QUIT:
                running = False  # Quitte le jeu si la fenêtre est fermée
                break
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False  # Quitte le jeu si la touche Esc est pressée
                    break
                elif ev.key == pygame.K_d:
                    # Touche 'd' pour proposer une nulle
                    who = "NOIR" if black_turn else "GRIS"
                    if drawProposal is None:
                        drawProposal = who  # Première proposition : enregistre le joueur
                    else:
                        if drawProposal != who:
                            screen.fill((220, 220, 220))
                            draw_board(screen)
                            for bpp2 in black_pieces:
                                draw_pawn(screen, bpp2, backend.PIECE_BLACK)
                            for gpp2 in gray_pieces:
                                draw_pawn(screen, gpp2, backend.PIECE_GRAY)
                            msg = font_menu.render("Nulle (accord mutuel)", True, (255, 0, 0))
                            screen.blit(msg, (screen_w // 2 - msg.get_width() // 2,
                                              screen_h // 2 - msg.get_height() // 2))
                            pygame.display.flip()
                            pygame.time.wait(2000)
                            running = False
                            break
                elif ev.key == pygame.K_s:
                    # Sauvegarde de la partie
                    backend.save_game_state("damestemp.json",
                                            black_pieces, gray_pieces, black_turn,
                                            black_caps, gray_caps,
                                            total_time, black_time, gray_time)
                    print("Partie sauvegardée dans damestemp.json")
                elif ev.key == pygame.K_l:
                    # Chargement d'une partie sauvegardée
                    loaded = backend.load_game_state("damestemp.json")
                    if loaded:
                        (black_pieces, gray_pieces, black_turn,
                         black_caps, gray_caps,
                         total_time, black_time, gray_time) = loaded
                        print("Partie chargée !")
                    else:
                        print("Échec du chargement.")
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos  # Récupère la position du clic de la souris
                cell = cell_from_mouse(mx, my)  # Convertit la position du clic en coordonnées de case
                if cell:
                    if not selectedPawn:
                        arr, idx = find_piece_at(cell, black_pieces, gray_pieces)
                        if arr:
                            pieceObj = arr[idx]  # Récupère la pièce sur la case cliquée
                            pieceCol = backend.PIECE_BLACK if arr == black_pieces else backend.PIECE_GRAY
                            if pieceCol == colorNow:  # Vérifie que la pièce appartient au joueur actif
                                if continuingCap:
                                    if pieceObj == capturingPiece:
                                        selectedPawn = (arr, idx)
                                else:
                                    allMov = backend.find_all_possible_moves(colorNow, black_pieces, gray_pieces)
                                    if mustCapture:
                                        allMov = [mm for mm in allMov if
                                                  mm['type'] == 'capture' and mm['piece'] == pieceObj]
                                    else:
                                        allMov = [mm for mm in allMov if mm['piece'] == pieceObj]
                                    if any(mv['type'] == 'capture' for mv in allMov):
                                        allMov = backend.break_down_captures(allMov, pieceObj)
                                    if allMov:
                                        selectedPawn = (arr, idx)
                                        possibleMoves = allMov
                    else:
                        chosenMv = None
                        # Parcourt les coups possibles pour vérifier si la destination cliquée correspond à un mouvement valide
                        for mv in possibleMoves:
                            if mv['dest'] == cell:
                                chosenMv = mv
                                break
                        if chosenMv:
                            p_ = chosenMv['piece']  # Récupère la pièce concernée par le mouvement
                            startPos = (p_[0], p_[1])  # Position de départ de la pièce
                            endPos = (chosenMv['dest'][0], chosenMv['dest'][1])  # Destination
                            animate_move(screen, p_, startPos, endPos, steps=10)  # Anime le déplacement
                            c_ = backend.PIECE_BLACK if p_ in black_pieces else backend.PIECE_GRAY
                            black_caps, gray_caps = backend.apply_move(chosenMv, black_pieces, gray_pieces,
                                                                       c_, black_caps, gray_caps)
                            if chosenMv['type'] == 'capture':
                                seq_ = backend.find_all_possible_moves(c_, black_pieces, gray_pieces)
                                seq_ = [xx for xx in seq_ if xx['piece'] == p_ and xx['type'] == 'capture']
                                if seq_:
                                    seq_ = backend.break_down_captures(seq_, p_)
                                    continuingCap = True
                                    capturingPiece = p_
                                    if capturingPiece in black_pieces:
                                        selectedPawn = (black_pieces, black_pieces.index(capturingPiece))
                                    else:
                                        selectedPawn = (gray_pieces, gray_pieces.index(capturingPiece))
                                    possibleMoves = seq_
                                else:
                                    continuingCap = False
                                    capturingPiece = None
                                    black_turn = not black_turn
                                    backend.update_position_history(black_pieces, gray_pieces, black_turn)
                                    selectedPawn = None
                                    possibleMoves = []
                            else:
                                continuingCap = False
                                capturingPiece = None
                                black_turn = not black_turn
                                backend.update_position_history(black_pieces, gray_pieces, black_turn)
                                selectedPawn = None
                                possibleMoves = []
                        else:
                            arr2, idx2 = find_piece_at(cell, black_pieces, gray_pieces)
                            if arr2:
                                piece2 = arr2[idx2]
                                col2 = backend.PIECE_BLACK if arr2 == black_pieces else backend.PIECE_GRAY
                                if col2 == colorNow:
                                    if continuingCap and piece2 == capturingPiece:
                                        selectedPawn = (arr2, idx2)
                                    else:
                                        newAll = backend.find_all_possible_moves(colorNow, black_pieces, gray_pieces)
                                        if mustCapture:
                                            newAll = [yy for yy in newAll if
                                                      yy['type'] == 'capture' and yy['piece'] == piece2]
                                        else:
                                            newAll = [yy for yy in newAll if yy['piece'] == piece2]
                                        if any(zz['type'] == 'capture' for zz in newAll):
                                            newAll = backend.break_down_captures(newAll, piece2)
                                        if newAll:
                                            selectedPawn = (arr2, idx2)
                                            possibleMoves = newAll

    # Fin de la partie : affiche le menu de fin avec le résumé des statistiques
    show_end_menu(screen,
                  black_name, gray_name,
                  black_time, gray_time, total_time,
                  black_pieces, gray_pieces,
                  black_caps, gray_caps)

    pygame.quit()  # Ferme Pygame proprement lorsque le jeu est terminé
