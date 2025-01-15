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
