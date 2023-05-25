import os
import sys
from typing import List, Tuple
import numpy as np
import time
import curses # pip install windows-curses
from curses import ascii

# Entrée du fichier grid
#while not os.path.isfile(input_path := input('Entrer le chemin vers le fichier grid: \n> ').strip('"')): 
#  print('Chemin du fichier invalide, veuillez réessayer.')

input_path = os.path.abspath("D:\Bureau\Test Sysnav\data\grids\grid3.txt")

"""
Initialisation des variables globales
"""
path = []                   # Contient le chemin calculé à chaque pas de temps
final_path = []             # Contient le chemin final que S parcourt
result = ''                 # Résultat
pause = True                # État de pause
terminated = False          # État de la recherche de solution

ground = []                 # Contient la grille représentant le terrain
exits = []                  # Contient les coordonnées des sorties
fires = []                  # Contient uniquement les derniers feux générés au pas de temps précédent
perso = (None, None)        # Contient la position du personnage

# On choisit d'imbriquer une classe dans le script pour sa praticité d'utilisation. On peut très bien le substituer par un dictionnaire.
class Move:                 
    """                     
    Structure d'un mouvement
    Un move contient :
        name : 'U', 'R', 'L', 'D',
        step : numéro de l'étape,
        position : (i,j) sur la grille,
        heuristic : calculé avec compute_heuristic()
        previous : contient le mouvement précédent, il permet de remonter le chemin parcouru pour la solution
    """
    def __init__(self, name, step, position, previous):
        self.name = name
        self.step = step
        self.position = position
        self.heuristic = compute_heuristic(position)
        self.previous = previous 

    def get_possible_moves(self) -> List:
        """
        Liste répertoriant les nouveaux mouvements possibles (URDL)
        
        Retourne: possible_moves = [liste des mouvements explorés et possibles]
        """
        i, j = self.position
        possible_moves = []
        movable = ['.','E','S']
        if j+1 < len(ground[i]) and ground[i][j+1] in movable:              # Case libre sur la droite: R    ground[i][j+1] : '.' -> 'S'
            possible_moves.append(Move('R', self.step+1, (i, j+1), self))
        if j > 0 and ground[i][j-1] in movable:                             # Case libre sur la gauche: L    ground[i][j-1] : '.' -> 'S'
            possible_moves.append(Move('L', self.step+1, (i, j-1), self))
        if i > 0 and ground[i-1][j] in movable:                             # Case libre au dessus:     U    ground[i-1][j] : '.' -> 'S'
            possible_moves.append(Move('U', self.step+1, (i-1, j), self))
        if i+1 < len(ground) and ground[i+1][j] in movable:                 # Case libre au dessous:    D    ground[i+1][j] : '.' -> 'S'
            possible_moves.append(Move('D', self.step+1, (i+1, j), self))
        return possible_moves

def read_file():
    """
    Lit le fichier et sauvegarde la grille dans `ground`
    Enregistre la position des feux, des sorties, et du personnage

    Modifie `ground`, `exits`, `fires`, `perso`
    """
    global perso
    with open(input_path, 'r') as file:
        for i, line in enumerate(file):
            if 'E' in line:
                exits.append((i, line.index('E')))
            if 'S' in line:
                perso = (i, line.index('S'))
            if 'F' in line:
                fires.append((i, line.index('F')))
            ground.append(line)

def compute_heuristic(pos) -> float:
    """
    Calcule l'heuristique à position donnée:
    Heuristique h = max( dist(exit, fire) - dist(exit, perso) ) parmi les exits et les fires
    Permet de choisir la sortie à prendre et à s'orienter sur le chemin

    Paramètre : pos = une position (i,j)
    Retourne  : heuristique de pos (float)
    """
    heuristics = []
    for i, exit in enumerate(exits): 
        dist_SE = np.sqrt((exit[0]-pos[0])**2 + (exit[1]-pos[1])**2)            # La distance SE[i]
        for j, fire in enumerate(fires):
            dist_EF = np.sqrt((fire[0]-exit[0])**2 + (fire[1]-exit[1])**2)      # La distance E[i]F[j]
            dist_SF = np.sqrt((fire[0]-pos[0])**2 + (fire[1]-pos[1])**2)
            heuristics.append(dist_SF+dist_EF-2*dist_SE)                        # Heuristique : max( SF + EF - 2*SE )
    return max(heuristics)

def update_solution(screen):
    """
    Cherche une solution de S vers une sortie et la met dans la variable `path`
    On effectue une recherche heuristique avec l'algorithme de recherche best-first

    La solution est contenue dans `path (List[Move])`
    """
    global path
    start = path[0]
    attempted_moves = [start]                           # Contient les mouvements tentés par S, quitte à revenir sur d'anciens mouvements possibles
    possible_moves = start.get_possible_moves()         # Contient tous les mouvements possibles sur le parcours de S

    while len(possible_moves) != 0:

        # On choisit le mouvement avec l'heuristique max parmis les mouvements possibles (les anciens explorés et les nouveaux)
        heuristics = [move.heuristic for move in possible_moves]
        chosen_move = possible_moves[np.argmax(heuristics)]

        # Si le personnage arrive sur la sortie, on retrace le chemin à l'envers
        if chosen_move.position in exits:
            attempted_moves.append(chosen_move)

            # Parcours à l'envers pour obtenir le chemin correct
            path = [chosen_move]
            while path[-1].previous is not start:
                path.append(path[-1].previous)
            path = path[::-1]
            return
        
        # On passe chosen_move def possible_moves à attempted_moves
        possible_moves.remove(chosen_move)
        attempted_moves.append(chosen_move)

        # On ajoute les nouveaux mouvements
        possible_moves_positions = [move.position for move in possible_moves]
        attempted_moves_positions = [move.position for move in attempted_moves]
        next_moves = chosen_move.get_possible_moves()
        for next in next_moves:
            if (next.position not in possible_moves_positions) and (next.position not in attempted_moves_positions):
                    possible_moves_positions.append(next.position)
                    possible_moves.append(next)                
                 
def update_perso():
    """
    Met à jour la position du personnage sur la grille
    Parcourt les cases voisines et calcule leur heuristique
    Le personnage se déplacera sur celle avec la meilleure heuristique

    Modifie `ground`
    """
    global final_path, perso, pause, terminated, result   
    final_path.append(path[0])
    perso = final_path[-1].position                                 # Perso bouge à la nouvelle position
    k, l = final_path[-1].position
    i, j = final_path[-2].position
    ground[k] = ground[k][:l] + 'S' + ground[k][l+1:]               
    ground[i] = ground[i][:j] + '.' + ground[i][j+1:]               # Libre après movement:      ground[i][j]   : 'S' -> '.'
    
    if perso in exits:                                              # Cas où le perso atteint la sortie
        ground[k] = ground[k][:l] + 'E' + ground[k][l+1:]  
        pause = True
        terminated = True
        result = ''.join([move.name for move in final_path[1:]])
    if perso in fires:                                              # Cas où le perso n'atteint pas la sortie et brûle
        pause = True
        terminated = True
        result = 'Échec'

def update_fire():
    """
    Met à jour la propagation du feu sur la grille `ground`
    Une case feu F enflamme les 4 cases avoisinantes

    Modifie `ground` et `fires`
    """
    global fires
    next_fires = []
    for fire in fires:                      # fires stocke les feux créés à la dernière étapte uniquement. 
        flammable = ['#','.','S']
        i, j = fire
        if j < len(ground[i])-1 and ground[i][j+1] in flammable:
            ground[i] = ground[i][:j+1] + 'F' + ground[i][j+2:]         # Arbre au dessus:      ground[i][j+1] : '#' -> 'F' 
            next_fires.append((i, j+1))
        if j > 0 and ground[i][j-1]  in flammable:                              
            ground[i] = ground[i][:j-1] + 'F' + ground[i][j:]           # Arbre en dessous:     ground[i][j-1] : '#' -> 'F'
            next_fires.append((i, j-1))
        if i < len(ground)-1 and ground[i+1][j]  in flammable:         
            ground[i+1] = ground[i+1][:j] + 'F' + ground[i+1][j+1:]     # Arbre sur la droite:  ground[i+1][j] : '#' -> 'F'
            next_fires.append((i+1, j))
        if i > 0 and ground[i-1][j]  in flammable:
            ground[i-1] = ground[i-1][:j] + 'F' + ground[i-1][j+1:]     # Arbre sur la gauche:  ground[i-1][j] : '#' -> 'F'
            next_fires.append((i-1, j))
    fires = next_fires.copy()                # fires stocke les feux nouvellement créés

def refresh_display(screen):
    """
    Actualise l'affichage dans le terminal avec `curses` dans le terminal
    """
    screen.clear()
    try:
    # Affichage de la grille actualisé
        height, width = screen.getmaxyx()
        step = final_path[-1].step
        for i in range(len(ground)):
            for j in range(len(ground[0])):
                char = ground[i][j]
                screen.addstr(i + (height - len(ground)) // 2, j + (width - len(ground[0])) // 2, char)

        # Affichage de l'aide
        if terminated:
            screen.addstr(1, 10, '(Terminé)')
            screen.addstr(0, 25, '>>> Résultat = ' + str(result))
            screen.addstr(1, 25, '>>> Appuyer sur Espace pour quitter')
        else:
            screen.addstr(4, 0, 'Espace : Pause/Play')
            screen.addstr(3, 0, 'Échap : Quitter' )
            if pause:
                screen.addstr(1, 25, '>>> Appuyer sur Espace pour lancer la simulation')
                screen.addstr(1, 10, '(Pause)')
            else:
                screen.addstr(1, 10, '(Play)')
        screen.addstr(0, 0, 'Best-First Search')
        screen.addstr(1, 0, 'Étape ' + str(step))

        for p in path:
            i, j = p.position
            if ground[i][j] not in ['S','E']:
                screen.addstr(i + (height - len(ground)) // 2, j + (width - len(ground[0])) // 2, 'P')

        screen.refresh()
    
    # Au cas où le terminal est trop petit
    except curses.error as e:
        print(f"ERREUR : Le terminal est trop petit pour afficher la grille : {e}")
        exit(1)

def pause_input(screen):
    """
    Permet les actions aux clavier.
    À utiliser avec l'option `curses.nodelay(False)`
    """
    global pause
    screen.nodelay(not pause)                   # Bascule pause/play de l'affichage, selon `pause`
    if((key := screen.getch()) != curses.ERR):  # Si une touche est appuyé
        if key == ascii.SP:                     # Appuie sur Espace pour mettre en pause
            screen.nodelay(not pause)           # Bascule pause / play
            pause = not pause 
        elif key == ascii.ESC:                  # Appuie sur Echap pour quitter
            if not terminated:
                print('Interruption du programme')
            exit(1)                             # Sort du programme 

def main(screen):
    """
    Programme principal
    """
    read_file()
    global path, final_path
    curses.curs_set(0)          # Enlève le curseur 
    start = Move('S', 0, perso, None)
    path = [start]  
    final_path = [start]
    # Boucle d'affichage
    while True:

        if '--nodisplay' not in sys.argv:
            refresh_display(screen)
            time.sleep(0.2)
            pause_input(screen)
        if terminated:          # Si l'algo est terminé, sortir et print le résultat ave l'exit code 0
            screen.clear()      
            print(result)
            if result == 'Échec':
                exit(1)
            exit(0)

        update_solution(screen)
        update_perso()
        update_fire()  

"""
Lance le terminal autour de la fonction main (ouverture et fermeture du terminal)
"""
curses.wrapper(main)
