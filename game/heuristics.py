class Heuristic:
    """
    Osnovna klasa za sve heuristike.
    """
    def get_evaluation(self, state, goal_state, size):
        """
        Procena stanja u odnosu na ciljno stanje.
        """
        raise NotImplementedError("Metoda nije implementirana!")


class HammingHeuristic(Heuristic):
    """
    Hamming heuristika: Broj pločica koje nisu na ciljnim pozicijama.
    """
    def get_evaluation(self, state, goal_state, size):
        return sum(1 for s, g in zip(state, goal_state) if s != g and s != 0)


class ManhattanHeuristic(Heuristic):
    """
    Manhattan heuristika: Suma Manhattan distanci za svaku pločicu.
    """
    def get_evaluation(self, state, goal_state, size):
        distance = 0
        for tile in range(len(state)):
            if state[tile] != 0:
                goal_index = goal_state.index(state[tile])  
                x1, y1 = divmod(tile, size)  
                x2, y2 = divmod(goal_index, size)  
                distance += abs(x1 - x2) + abs(y1 - y2)  
        return distance
