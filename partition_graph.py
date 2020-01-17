#! /usr/bin/python

import gurobipy


def build_model(graph, blocks):
    model = gurobipy.Model()
    size_x = len(graph)
    subset_vars = model.addVars(
        (
            (i, j, k)
            for i in range(size_x)
            for j in range(size_x)
            for k in range(blocks)
            if graph[i][j]
        ),
        vtype=gurobipy.GRB.BINARY,
    )
    arc_vars = model.addVars(
        ((i, j) for i in range(size_x) for j in range(size_x) if graph[i][j]),
        vtype=gurobipy.GRB.BINARY,
    )

    node_vars = model.addVars(
        ((j, k) for j in range(size_x) for k in range(blocks)), vtype=gurobipy.GRB.BINARY
    )

    model.addConstrs((gurobipy.quicksum(subset_vars[i, j, k] for i in range(size_x) if graph[i][j]) == node_vars[j, k])
    for j in range(size_x) for k in range(blocks))

    model.addConstrs((gurobipy.quicksum(subset_vars[j, i, k] for i in range(size_x) if graph[i][j]) == node_vars[j, k])
    for j in range(size_x) for k in range(blocks))

    for i in range(size_x):
        model.addConstrs((gurobipy.quicksum(node_vars[j, k] for k in range(blocks)) == 1) for j in range(size_x) if graph[i][j])



    model.setObjective(
        gurobipy.quicksum(
            subset_vars[i, j, k] * graph[i][j]
            for i in range(size_x)
            for j in range(size_x)
            for k in range(blocks)
            if graph[i][j]
        ),
        sense=gurobipy.GRB.MINIMIZE,
    )

    model.optimize()
    for k, v in subset_vars.items():
        if v.x:
            print(k)


def main():
    graph = [
        [0, 1, 1, 10, 0, 0],
        [1, 0, 1, 0, 0, 10],
        [1, 1, 0, 0, 10, 0],
        [10, 0, 0, 0, 1, 1],
        [0, 0, 10, 1, 0, 1],
        [0, 10, 0, 1, 1, 0],
    ]
    blocks = 2
    build_model(graph, blocks)


if __name__ == "__main__":
    main()
