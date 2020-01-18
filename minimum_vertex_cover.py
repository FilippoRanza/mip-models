#! /usr/bin/python

from argparse import ArgumentParser
import gurobipy

def build_model(graph: [(int, int)], costs: [int], verbose) -> gurobipy.Model:
    env = gurobipy.Env()
    env.setParam("MIPGap", 1e-12)
    if verbose:
        env.setParam("OutputFlag", 0)
    model = gurobipy.Model(env=env)
    node_vars = model.addVars((i for i in range(len(costs))), vtype=gurobipy.GRB.BINARY)
    for i, j in graph:
        model.addConstr(node_vars[i] + node_vars[j] >= 1)

    model.setObjective(gurobipy.quicksum(
        (node_vars[i] * costs[i] for i in range(len(costs)))
        ),
        sense=gurobipy.GRB.MINIMIZE)
    model.update()
    return model


def solve_model(model: gurobipy.Model):
    model.optimize()
    if model.getAttr("STATUS") != gurobipy.GRB.OPTIMAL:
        raise ValueError
    sol = model.getVars()
    out = ""
    value = 0
    for v in sol:
        out += f"{v.VarName} {v.X}\n"
        value += 1 if v.X >= 0.5 else 0

    return out, value    

def build_polygon_graph(size) : 
    edges = [
        (i, (i + 1) % size) 
        for i in range(size)
    ]
    costs = [1] * size
    return edges, costs

def build_clique_graph(size):
    edges = [
        (i, j)
        for i in range(size) 
        for j in range(i)
    ]
    costs = [1] * size
    return edges, costs


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    
    mutex_args = parser.add_mutually_exclusive_group(required=True)
    mutex_args.add_argument('-c', '--clique', type=int)
    mutex_args.add_argument('-p', '--polygon', type=int)

    return parser.parse_args()


def main():    
    args = parse_args()
    print(args)
    if args.polygon:
        edges, costs = build_polygon_graph(args.polygon)
    else:
        edges, costs = build_clique_graph(args.clique)

    model = build_model(edges, costs, args.verbose)
    relax = model.relax()
    relax_sol, round_val = solve_model(relax)
    int_sol, int_val = solve_model(model)
    print("Relax")
    print(relax_sol)
    print("Int")
    print(int_sol)

    print(f"Relax {round_val}, Int {int_val}, Ratio {round_val / int_val} ")




if __name__ == "__main__":
    main()
