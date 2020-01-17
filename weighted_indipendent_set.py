#! /usr/bin/python

import gurobipy

def build_model(values, connections):
    model = gurobipy.Model()
    
    set_vars = model.addVars(
        (i for i in range(len(values))), vtype=gurobipy.GRB.BINARY
    )


    model.addConstrs(
        ((set_vars[i] + set_vars[j]) <= 1)
        for i, j in connections
    )

    model.setObjective(
        gurobipy.quicksum(set_vars[i] * w for i, w in enumerate(values)),
        sense=gurobipy.GRB.MAXIMIZE   
    )

    model.optimize()
    return model


def main():
    values = [5, 2, 4, 7, 6]
    connections = [(0, 1), (1, 2), (0, 2), (1, 3), (0, 4)]

    model = build_model(values, connections)
    sol = model.getVars()
    for v in sol:
        print(v)


if __name__ == "__main__":
    main()
