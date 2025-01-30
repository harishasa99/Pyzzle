import numpy as np

def get_pos_2d(index_1d, size):
    """Pretvara 1D indeks u 2D koordinatu."""
    return index_1d // size, index_1d % size


def get_inversion_count(state):
    """Računa broj inverzija u zadatom stanju."""
    inversion_count = 0
    for i in range(len(state)):
        for j in range(i + 1, len(state)):
            if state[i] and state[j] and state[i] > state[j]:  # Preskačemo prazan prostor (0)
                inversion_count += 1
    return inversion_count


def is_solvable(state, size):
    """Proverava da li je zadato stanje rešivo."""
    inversions = get_inversion_count(state)
    empty_row = state.index(0) // size  # Indeks reda u kojem je prazno polje

    if size % 2 == 1:
        # Grid neparne dimenzije (3x3, 5x5...) -> Inversions mora biti paran broj
        return inversions % 2 == 0
    else:
        # Grid parne dimenzije (4x4, 6x6...) -> Specijalno pravilo
        return (inversions + empty_row) % 2 == 1


def get_init_and_goal_states(size=3, seed=123):
    """
    Generiše početno i ciljno stanje koje je rešivo.
    Podržava i 3x3 i 4x4 slagalice.
    """
    np.random.seed(seed)
    goal_state = tuple(range(1, size ** 2)) + (0,)  # Ciljno stanje

    while True:
        initial_state = list(goal_state)
        np.random.shuffle(initial_state)  # Mešamo pločice
        if is_solvable(initial_state, size) and tuple(initial_state) != goal_state:
            break  # Kada pronađemo rešivo stanje, prekidamo petlju

    return tuple(initial_state), goal_state
