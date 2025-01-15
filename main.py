"""
Nom : Backend.py
Auteurs : Dylan, Samuel
Date 11.11.2024
"""
###############################################################################
# Point d'entrée pour lancer le jeu de dames.
# - Import de frontend (interface)
# - Appelle frontend.run_game()
###############################################################################

import pygame       # On importe pygame pour gérer l'affichage et les événements
import frontend     # On importe le frontend qui gère l'interface graphique

if __name__ == "__main__":           # Si ce fichier est exécuté directement (et non importé)
    frontend.run_game()             # On lance le jeu en appelant la boucle principale du frontend
    pygame.quit()                   # Une fois le jeu terminé, on ferme Pygame proprement