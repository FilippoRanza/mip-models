#! /usr/bin/python

from secrets import randbelow
from time import time_ns
import gurobipy

def update_value(items, capacity, off, on, curr_val, curr_cap):
    (p_on, w_on) = items[on]
    (p_off, w_off) = items[off]

    tmp_cap = curr_cap - w_off + w_on
    if tmp_cap > capacity:
        return -1, curr_cap

    tmp_val = curr_val - p_off + p_on
    return tmp_val, tmp_cap


def compute_value(items, selected):
    value = 0
    price = 0
    for s, (p, w) in zip(selected, items):
        if s:
            price += p
            value += w
    return price, value


def initialize(items, capacity):
    value = 0
    for i, (_, w) in enumerate(items):
        if w + value < capacity:
            value += w
            yield True
        else:
            yield False

def find_next_best(items, capacity, selected, current_val, current_cap):
    stat = False
    gen = ((i, j ) for i, s_i in enumerate(selected) for j, s_j in enumerate(selected) if s_i and not s_j)
    for i, j in gen:
            tmp_val, tmp_cap = update_value(items, capacity, i, j, current_val, current_cap)
            if tmp_val >= current_val:
                selected[i] = False
                selected[j] = True
                stat = True
                current_cap = tmp_cap
                break

    return stat, current_val, current_cap


def one_bit_flip(items, capacity):
    items.sort(key=lambda x: -x[0])
    selected = list(initialize(items, capacity))
    current_val, current_cap = compute_value(items, selected)
    remove = True
    while True:
        stat, current_val, current_cap = find_next_best(items, capacity, selected, current_val, current_cap)
        if not stat:
            break

    return selected, current_val

def random_knapsack(size):
    top = size * 5
    items = [(randbelow(top) + 1, randbelow(top) + 1) for _ in range(size)]
    capacity = randbelow(size * 10) + top
    return items, capacity

def exact_solution(items, capacity):
    env = gurobipy.Env()
    env.setParam("OutputFlag", 0)
    model = gurobipy.Model(env=env)
    item_vars = model.addVars((i for i in range(len(items))), vtype=gurobipy.GRB.BINARY) 
    model.addConstr(
        gurobipy.quicksum(item_vars[i]*items[i][1] for i in range(len(items))) 
        <= capacity
    )

    model.setObjective(
        gurobipy.quicksum(item_vars[i]*items[i][0] for i in range(len(items))),
        sense=gurobipy.GRB.MAXIMIZE
    )

    model.optimize()
    return model.objVal

def main():
    #items, capacity = random_knapsack(600)
    items = [(40, 10), (10, 20), (20, 20), (5, 5), (10, 40), (30, 10), (45, 75)]
    capacity = 100
    print('ok')
    start = time_ns()
    selected, val = one_bit_flip(items, capacity)
    eur = time_ns() - start

    print(val)

    start = time_ns()
    val = exact_solution(items, capacity)
    exc = time_ns() - start

    print(val)
    if eur < exc:
        print("Euristic", (exc - eur) / 1e6)
    else:
        print("Gurobi", (eur - exc) / 1e6)


if __name__ == "__main__":
    main()

