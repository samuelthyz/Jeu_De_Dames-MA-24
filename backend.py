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


def move_piece(piece, dest):
    """
    Déplace la pièce à la nouvelle destination.
    """
    piece[0], piece[1] = dest[0], dest[1]  # Mise à jour des coordonnées


def apply_move(move, black_pieces, gray_pieces, color, black_caps, gray_caps):
    """
    Applique un coup (capture ou simple déplacement), met à jour le compteur de non-captures et les statistiques.
    - move : dictionnaire décrivant le coup
    - black_caps / gray_caps : captures effectuées par chaque camp.
    Retourne les compteurs mis à jour.
    """
    global no_capture_turns, game_stats
    piece = move['piece']  # On récupère la pièce à déplacer
    is_capture = (move.get('type') == 'capture')  # Vérifie si c'est une capture
    captured_count = 0  # Initialisation du compteur de captures

    game_stats["moves_count"] += 1  # On incrémente le nombre de coups joués

    if is_capture:  # Si c'est une capture
        enemies = gray_pieces if color == PIECE_BLACK else black_pieces  # Détermine l'adversaire
        before = len(enemies)  # Nombre d'ennemis avant capture
        for (rr, cc) in move['path']:  # Pour chaque position de capture
            enemies[:] = [x for x in enemies if not (x[0] == rr and x[1] == cc)]
            # On supprime l'ennemi capturé
        captured_count = before - len(enemies)  # Calcul du nombre de pièces capturées
        no_capture_turns = 0  # Réinitialisation du compteur pour capture
        if color == PIECE_BLACK:  # Mise à jour pour les noirs
            black_caps += captured_count
        else:  # Sinon pour les gris
            gray_caps += captured_count
        game_stats["total_captures"] += captured_count  # Ajoute au total des captures
    else:
        no_capture_turns += 1  # Coup simple : incrémente le compteur de non-captures

    move_piece(piece, move['dest'])  # Déplace la pièce
    promote_to_queen_if_needed(piece, color)  # Teste la promotion
    return black_caps, gray_caps  # Retourne les compteurs mis à jour


def explore_captures(piece, black_pieces, gray_pieces, color, captured_list):
    """
    Recherche récursive pour les captures multiples (pions ou dames).
    Retourne une liste de tuples (destination, nb_captures, path, nb_dames_capt).
    """
    found_capture = False  # Indique si une capture a été trouvée
    results = []  # Liste des résultats
    r, c, isQ = piece  # Décompose la pièce (row, col, is_dame)
    enemies = gray_pieces if color == PIECE_BLACK else black_pieces  # Définit les ennemis
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Directions possibles pour capturer

    if isQ:
        # Pour une dame
        for dr, dc in directions:  # Pour chaque direction
            step = 1  # Commence par un pas
            while True:
                nr = r + dr * step  # Calcul de la nouvelle ligne
                nc = c + dc * step  # Calcul de la nouvelle colonne
                if not is_in_bounds(nr, nc):  # Si en dehors du plateau
                    break  # On arrête cette direction
                if is_occupied(nr, nc, black_pieces, gray_pieces):  # Si une pièce est rencontrée
                    # Si c'est un pion ennemi et pas déjà capturé
                    if any(e[0] == nr and e[1] == nc for e in enemies) and (nr, nc) not in captured_list:
                        nr2, nc2 = nr + dr, nc + dc  # Case derrière l'ennemi
                        if is_in_bounds(nr2, nc2) and not is_occupied(nr2, nc2, black_pieces, gray_pieces):
                            oldpos = (piece[0], piece[1], piece[2])  # Enregistre la position d'origine
                            captured_p = [xx for xx in enemies if xx[0] == nr and xx[1] == nc][0]
                            # Récupère la pièce ennemie capturable
                            piece[0], piece[1] = nr2, nc2  # Déplace temporairement la dame
                            if color == PIECE_BLACK:
                                newB = black_pieces
                                newG = [g for g in gray_pieces if g != captured_p]  # Supprime l'ennemi capturé
                            else:
                                newB = [b for b in black_pieces if b != captured_p]
                                newG = gray_pieces
                            subcaps = explore_captures(piece, newB, newG, color, captured_list + [(nr, nc)])
                            # Exploration récursive pour capture multiple
                            qhit = 1 if captured_p[2] else 0  # Compte si c'était une dame adverse
                            if not subcaps:  # Si pas d'autres captures possibles
                                results.append(([nr2, nc2], 1, [(nr, nc)], qhit))
                            else:
                                for (dest, cn, path_, qC) in subcaps:
                                    results.append((dest, cn + 1, [(nr, nc)] + path_, qC + qhit))
                            piece[0], piece[1], piece[2] = oldpos  # Restaure la position initiale
                            found_capture = True  # Capture trouvée
                    break  # Arrête le déplacement dans cette direction
                step += 1  # Passe à la case suivante dans la direction
    else:
        # Pour un pion simple (non dame)
        for dr, dc in directions:  # Pour chaque direction diagonale
            mr = r + dr  # Case de mouvement intermédiaire
            mc = c + dc
            er = r + 2 * dr  # Destination après saut
            ec = c + 2 * dc
            if is_in_bounds(mr, mc) and is_in_bounds(er, ec):  # Vérifie que tout est dans les limites
                if any(e[0] == mr and e[1] == mc for e in enemies) and not is_occupied(er, ec, black_pieces,
                                                                                       gray_pieces):
                    # Si l'ennemi est bien à la bonne position et destination libre
                    if (mr, mc) not in captured_list:  # Et que cette capture n'a pas été déjà faite
                        old_ = (piece[0], piece[1], piece[2])  # Enregistre la position d'origine
                        capp_ = [xx for xx in enemies if xx[0] == mr and xx[1] == mc][0]
                        # Récupère l'ennemi à capturer
                        piece[0], piece[1] = er, ec  # Déplace temporairement la pièce
                        if color == PIECE_BLACK:
                            newB = black_pieces
                            newG = [gg for gg in gray_pieces if gg != capp_]
                        else:
                            newB = [bb for bb in black_pieces if bb != capp_]
                            newG = gray_pieces
                        subc = explore_captures(piece, newB, newG, color, captured_list + [(mr, mc)])
                        # Recherche récursive d'autres captures
                        qh = 1 if capp_[2] else 0  # Vérifie si la pièce capturée est une dame
                        if not subc:  # Si aucune capture supplémentaire
                            results.append(([er, ec], 1, [(mr, mc)], qh))
                        else:
                            for (dest, cn2, path2, qC2) in subc:
                                results.append((dest, cn2 + 1, [(mr, mc)] + path2, qC2 + qh))
                        piece[0], piece[1], piece[2] = old_  # Restaure la position d'origine
                        found_capture = True  # Capture trouvée
    if not found_capture:  # Si aucune capture trouvée
        return []  # Retourne une liste vide
    return results  # Retourne la liste des captures possibles


def can_capture(piece, black_pieces, gray_pieces, color):
    """
    Fonction simplifiée pour vérifier les captures pour une pièce.
    """
    return explore_captures(piece[:], black_pieces, gray_pieces, color, [])
    # Lance l'exploration sans historique de captures


def find_all_possible_moves(color, black_pieces, gray_pieces):
    """
    Rassemble tous les coups possibles pour le joueur donné.
    Les captures sont prioritaires sur les déplacements simples.
    """
    ally = black_pieces if color == PIECE_BLACK else gray_pieces
    captures = []  # Liste pour stocker les coups de capture
    normals = []  # Liste pour stocker les déplacements simples

    for pi in ally:  # Pour chaque pièce alliée
        subc = can_capture(pi, black_pieces, gray_pieces, color)
        for (dest, cnt, path_, qhit) in subc:
            captures.append({
                'piece': pi,
                'type': 'capture',  # Type de coup : capture
                'dest': dest,  # Destination finale de la capture
                'count': cnt,  # Nombre total de captures dans cette séquence
                'path': path_,  # Chemin des captures
                'isQueen': pi[2],  # Indique si la pièce est déjà une dame
                'queenCapt': qhit  # Nombre de captures de dames effectuées
            })
    if captures:  # Si au moins une capture est possible
        maxC = max(x['count'] for x in captures)  # On cherche le maximum de captures possibles
        best = [x for x in captures if x['count'] == maxC]  # On retient uniquement les meilleurs
        maxQ = max(x['queenCapt'] for x in best)  # Priorise la capture impliquant une dame adverse
        return [b for b in best if b['queenCapt'] == maxQ]  # Retourne la liste filtrée

    # Sinon, on cherche les déplacements simples
    for pc in ally:
        r, c, isQ = pc
        if isQ:  # Pour une dame
            dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in dirs:
                st = 1  # Pas initial
                while True:
                    nr = r + dr * st  # Calcul de la nouvelle position
                    nc = c + dc * st
                    if not is_in_bounds(nr, nc) or is_occupied(nr, nc, black_pieces, gray_pieces):
                        break  # On arrête dès que l'on sort du plateau ou que la case est occupée
                    normals.append({
                        'piece': pc,
                        'type': 'move',  # Type de coup : déplacement simple
                        'dest': [nr, nc],  # Destination
                        'count': 0,  # Pas de capture ici
                        'path': [],  # Chemin vide pour un déplacement
                        'isQueen': True,  # Confirme que la pièce est une dame
                        'queenCapt': 0  # Aucune capture de dame
                    })
                    st += 1  # Essai à la case suivante dans la même direction
        else:
            dFwd = 1 if color == PIECE_BLACK else -1  # Détermine le sens de déplacement selon la couleur
            for dC in [-1, 1]:  # Pour les diagonales gauche et droite
                nr = r + dFwd  # Calcul de la destination
                nc = c + dC
                if is_in_bounds(nr, nc) and not is_occupied(nr, nc, black_pieces, gray_pieces):
                    normals.append({
                        'piece': pc,
                        'type': 'move',
                        'dest': [nr, nc],
                        'count': 0,
                        'path': [],
                        'isQueen': False,  # Pion normal, pas une dame
                        'queenCapt': 0
                    })
    return normals  # Retourne les déplacements simples possibles


def break_down_captures(moves, piece):
    """
    Transforme les captures multiples en captures unitaires successives.
    Utile pour découper le coup en plusieurs étapes.
    """
    arr = []  # Liste pour stocker le résultat
    r0, c0, _ = piece  # Position de départ de la pièce
    for mv in moves:
        if mv['count'] > 1:  # Si plusieurs captures sont prévues
            fc = mv['path'][0]  # On prend la première capture du chemin
            dr = fc[0] - r0
            dc = fc[1] - c0
            nr = r0 + 2 * dr  # Nouvelle destination après capture simple
            nc = c0 + 2 * dc
            cp = mv.copy()  # Copie du dictionnaire pour modification
            cp['dest'] = [nr, nc]  # Mise à jour de la destination
            cp['path'] = [mv['path'][0]]  # Garde uniquement la première capture
            cp['count'] = 1  # Fixe le compte à 1 capture
            arr.append(cp)  # Ajoute à la liste
        else:
            arr.append(mv)  # Sinon, ajoute directement le coup
    return arr  # Retourne la liste des coups décomposés
