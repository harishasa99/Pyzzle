from collections import deque
import heapq

class Algorithm:
    def __init__(self, heuristic=None):
        self.heuristic = heuristic
        self.nodes_evaluated = 0
        self.nodes_generated = 0

    def get_legal_actions(self, state, size):
        """
        Generiše sve legalne poteze za trenutno stanje.
        """
        self.nodes_evaluated += 1
        max_index = len(state)
        zero_tile_ind = state.index(0)
        legal_actions = []

        # Pomeri gore
        if zero_tile_ind - size >= 0:
            legal_actions.append(zero_tile_ind - size)
        # Pomeri dole
        if zero_tile_ind + size < max_index:
            legal_actions.append(zero_tile_ind + size)
        # Pomeri levo
        if zero_tile_ind % size != 0:
            legal_actions.append(zero_tile_ind - 1)
        # Pomeri desno
        if (zero_tile_ind + 1) % size != 0:
            legal_actions.append(zero_tile_ind + 1)

        return legal_actions

    def apply_action(self, state, action):
        """
        Primena poteza na trenutno stanje.
        """
        self.nodes_generated += 1
        new_state = list(state)
        zero_tile_ind = state.index(0)

        # Zameni mesta nule i odabranog polja
        new_state[zero_tile_ind], new_state[action] = new_state[action], new_state[zero_tile_ind]

        return tuple(new_state)

    def get_steps(self, initial_state, goal_state, size):
        """
        Generiše korake od početnog do ciljnog stanja.
        """
        raise NotImplementedError("Metoda nije implementirana!")


class BFSAlgorithm(Algorithm):
    """
    Breadth-First Search (BFS) algoritam.
    """
    def get_steps(self, initial_state, goal_state, size):
        print(f"Solving {size}x{size} puzzle with BFSAlgorithm")

        # Ako je stanje već rešeno
        if initial_state == goal_state:
            print("✅ Already solved!")
            return []

        nodes = deque([(initial_state, [])])
        visited = {}  # Koristi dict za optimalno pretraživanje

        max_iterations = 100000  # Povećan broj iteracija za 4x4
        iteration = 0

        while nodes:
            if iteration > max_iterations:
                print("❌ BFS stopped: Too many iterations!")
                return []  # Ako pređe limit, prekini

            current_state, actions = nodes.popleft()
            iteration += 1

            if current_state == goal_state:
                print(f"✅ Solution found in {len(actions)} steps!")
                return actions

            visited.setdefault(current_state, len(actions))

            for action in self.get_legal_actions(current_state, size):
                new_state = self.apply_action(current_state, action)
                if new_state not in visited or len(actions) + 1 < visited[new_state]:
                    nodes.append((new_state, actions + [action]))
                    visited[new_state] = len(actions) + 1

        print("❌ No solution found!")
        return []




class BestFirstAlgorithm(Algorithm):
    """
    Greedy Best-First Search algoritam.
    """
    def get_steps(self, initial_state, goal_state, size):
        print(f"Solving {size}x{size} puzzle with Greedy Best-First Search")
        nodes = []
        visited = set()
        heuristic_value = self.heuristic.get_evaluation(initial_state, goal_state, size)
        heapq.heappush(nodes, (heuristic_value, (initial_state, [])))

        while nodes:
            _, (current_state, actions) = heapq.heappop(nodes)

            if current_state == goal_state:
                print(f"Solution found in {len(actions)} steps!")
                return actions

            visited.add(current_state)
            for action in self.get_legal_actions(current_state, size):
                new_state = self.apply_action(current_state, action)
                if new_state not in visited:
                    heuristic_value = self.heuristic.get_evaluation(new_state, goal_state, size)
                    heapq.heappush(nodes, (heuristic_value, (new_state, actions + [action])))
                    visited.add(new_state)

        print("❌ No solution found!")
        return []


class AStarAlgorithm(Algorithm):
    """
    A* algoritam.
    """
    def get_steps(self, initial_state, goal_state, size):
        print(f"Solving {size}x{size} puzzle with A* Algorithm")
        nodes = []
        visited = set()
        heuristic_value = self.heuristic.get_evaluation(initial_state, goal_state, size)
        heapq.heappush(nodes, (heuristic_value, (initial_state, [], 0)))  # (f_cost, (state, actions, g_cost))

        max_iterations = 50000  # Limit iteracija

        iteration = 0
        while nodes:
            if iteration > max_iterations:
                print("❌ A* stopped: Too many iterations!")
                return []  # Ako pređe limit, prekini

            _, (current_state, actions, g_cost) = heapq.heappop(nodes)
            iteration += 1

            if current_state == goal_state:
                print(f"✅ Solution found in {len(actions)} steps!")
                return actions

            visited.add(current_state)
            for action in self.get_legal_actions(current_state, size):
                new_state = self.apply_action(current_state, action)
                if new_state not in visited:
                    h_cost = self.heuristic.get_evaluation(new_state, goal_state, size)
                    f_cost = g_cost + 1 + h_cost
                    heapq.heappush(nodes, (f_cost, (new_state, actions + [action], g_cost + 1)))
                    visited.add(new_state)

        print("❌ A* failed to find a solution!")
        return []

