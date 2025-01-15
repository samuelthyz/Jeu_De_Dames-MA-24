"""
Nom : Backend.py
Auteurs : Dylan, Samuel
Date 11.11.2024
"""
###############################################################################
# Logique du jeu de Dames 10x10 (règles suisses).
#
# - 50 coups sans capture (no_capture_turns)
# - Historique de positions (positions_history) pour nulle par répétition
# - Captures, promotions, find_all_possible_moves, etc.
# - Statistiques (moves_count, total_captures) : game_stats
# - Sauvegarde/Chargement (JSON)
###############################################################################

import json  # Import de json pour la sauvegarde et le chargement

# Couleurs logiques des pions
PIECE_BLACK = (10, 10, 10)  # On définit la couleur noire : plus visible !
PIECE_GRAY = (200, 200, 200)  # Définition de la couleur grise
PIECE_QUEEN = (250, 250, 0)  # Pour la dame, on utilise un jaune vif

# Variables globales du jeu
no_capture_turns = 0  # Compteur des coups sans capture (pour règle des 50 coups)
positions_history = {}  # Historique des positions sous forme de dictionnaire
current_player_color = PIECE_BLACK  # Couleur du joueur actuel, on commence par les noirs

# Statistiques globales du jeu
game_stats = {
    "moves_count": 0,  # Total des coups joués (initialisé à zéro)
    "total_captures": 0  # Total des captures effectuées
}


def reset_game_state():
    """
    Réinitialise l'état global avant le début d'une nouvelle partie.
    (Remise à zéro du compteur de 50 coups, historique, stats, etc.)
    """
    global no_capture_turns, positions_history, current_player_color, game_stats
    no_capture_turns = 0  # On remet le compteur à zéro
    positions_history.clear()  # On vide l'historique des positions
    current_player_color = PIECE_BLACK  # On remet le joueur actif aux noirs
    game_stats = {  # Réinitialisation des statistiques
        "moves_count": 0,
        "total_captures": 0
    }


def check_winner(black_pieces, gray_pieces):
    """
    Vérifie si un camp a perdu toutes ses pièces.
    Retourne 'GRIS' si aucune pièce noire, 'NOIR' si aucune pièce grise,
    ou None si la partie continue.
    """
    if not black_pieces:  # Si la liste des pièces noires est vide
        return "GRIS"  # Les gris remportent la partie
    if not gray_pieces:  # Sinon, si les pièces grises sont absentes
        return "NOIR"  # Les noirs gagnent
    return None  # Sinon, pas de gagnant pour l'instant


def create_position_key(black_pieces, gray_pieces, is_black_turn):
    """
    Crée une clé unique représentant l'état du plateau.
    On trie les positions pour que la comparaison soit fiable.
    """
    sb = tuple(sorted(tuple(b) for b in black_pieces))  # Tri des positions noires
    sg = tuple(sorted(tuple(g) for g in gray_pieces))  # Tri des positions grises
    return (sb, sg, is_black_turn)  # Retourne le tuple clé


def update_position_history(black_pieces, gray_pieces, is_black_turn):
    """
    Met à jour l'historique des positions en incrémentant le compteur.
    """
    global positions_history
    key = create_position_key(black_pieces, gray_pieces, is_black_turn)  # Création de la clé
    positions_history[key] = positions_history.get(key, 0) + 1  # Incrémente ou initialise à 1


def is_repeated_position(black_pieces, gray_pieces, is_black_turn):
    """
    Vérifie si la position courante a déjà été atteinte 3 fois,
    ce qui indique une situation de nulle.
    """
    key = create_position_key(black_pieces, gray_pieces, is_black_turn)  # Création de la clé
    return positions_history.get(key, 0) >= 3  # Retourne True si comptage >= 3


def is_in_bounds(row, col):
    """
    Vérifie si la case (row, col) se trouve dans le plateau de 10x10.
    """
    return 0 <= row < 10 and 0 <= col < 10  # Test des bornes


def is_occupied(row, col, black_pieces, gray_pieces):
    """
    Vérifie si une case (row, col) est occupée par un pion (noir ou gris).
    """
    for pc in black_pieces + gray_pieces:  # Parcours de toutes les pièces
        if pc[0] == row and pc[1] == col:  # Si la position correspond
            return True  # Retourne True (occupée)
    return False  # Sinon, la case est libre


def promote_to_queen_if_needed(piece, color):
    """
    Promotion : si un pion atteint la dernière rangée, il devient dame.
    On réinitialise aussi le compteur de coups sans capture.
    """
    global no_capture_turns
    if color == PIECE_BLACK and piece[0] == 9:  # Si pion noir atteint la dernière ligne
        piece[2] = True  # Il devient dame
    if color == PIECE_GRAY and piece[0] == 0:  # Si pion gris atteint la première ligne
        piece[2] = True  # Il est promu
    if piece[2]:  # Si la pièce est devenue dame
        no_capture_turns = 0  # On réinitialise le compteur de non-captures
