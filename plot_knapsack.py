#! /usr/bin/python

from matplotlib import pyplot as plt

from flip_bit_knapsack import one_bit_flip

def all_solution(items):
    for i in range(2**items):
        yield (bool(i & (1 << j))  for j in range(items))

def eval_solution(items, solution, capacity):
    val = 0
    cap = 0
    for s, (p, w) in zip(solution, items):
        if s:
            cap += w
            if cap > capacity:
                return -1
            val += p
    return val


def feasible_solutions(items, capacity):
    for sol in all_solution(len(items)):
        val = eval_solution(items, sol, capacity)
        if val != -1:
            yield val
        

def main():
    capacity = 100
    items = [(40, 40), (60, 50), (10, 30), (10, 10), (3, 10), (20, 40), (60, 30)]

    solutions = list(feasible_solutions(items, capacity))
    plt.plot(solutions, '*-')
    plt.show()


if __name__ == "__main__":
    main()
