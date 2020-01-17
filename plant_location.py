#! /usr/bin/python

from argparse import ArgumentParser
from json import dump
from secrets import randbelow

import gurobipy


class Place:
    def __init__(self, size_x, size_y):
        self.x = randbelow(size_x)
        self.y = randbelow(size_y)

    def distance(self, other):
        x = (self.x - other.x) ** 2
        y = (self.y - other.y) ** 2
        return (x + y) ** 2


def random_set(count, callback, *args):
    out = set()
    while len(out) != count:
        tmp = callback(*args)
        out.add(tmp)
    return out


def random_map(plants, customers, size_x, size_y):
    rnd_plants = random_set(plants, Place, size_x, size_y)
    rnd_customers = random_set(customers, Place, size_x, size_y)

    service_cost = [
        [cust.distance(plant) for plant in rnd_plants] for cust in rnd_customers
    ]
    open_cost = list(
        random_set(
            plants, lambda x, y: (randbelow(x) + y) / 3, 15 * plants, (size_x * size_y)
        )
    )
    return open_cost, service_cost


def random_instance(plants, customers):
    open_cost = [randbelow(15 * plants) for _ in range(plants)]
    service_cost = [
        [randbelow(10 * (plants + customers)) for _ in range(plants)]
        for _ in range(customers)
    ]
    return open_cost, service_cost


def base_model(open_cost, service_cost, verbose):
    env = gurobipy.Env()
    env.setParam("MIPGap", 1e-12)
    if not verbose:
        env.setParam("OutputFlag", 0)
    model = gurobipy.Model(env=env)
    plants = len(open_cost)
    customer = len(service_cost)
    service_vars = model.addVars(
        ((i, j) for j in range(plants) for i in range(customer)),
        vtype=gurobipy.GRB.BINARY,
    )
    open_vars = model.addVars((j for j in range(plants)), vtype=gurobipy.GRB.BINARY)

    model.addConstrs(
        gurobipy.quicksum(service_vars[i, j] for j in range(plants)) == 1
        for i in range(customer)
    )

    model.setObjective(
        (
            gurobipy.quicksum(open_cost[j] * open_vars[j] for j in range(plants))
            + gurobipy.quicksum(
                service_cost[i][j] * service_vars[i, j]
                for i in range(customer)
                for j in range(plants)
            )
        ),
        sense=gurobipy.GRB.MINIMIZE,
    )

    return model, service_vars, open_vars


def model_a(open_cost, service_cost, verbose):
    model, service_vars, open_vars = base_model(open_cost, service_cost, verbose)
    clients = len(service_cost)
    plants = len(open_cost)
    model.addConstrs(
        gurobipy.quicksum(service_vars[i, j] for i in range(clients))
        <= (clients * open_vars[j])
        for j in range(plants)
    )

    return model, service_vars, open_vars


def model_b(open_cost, service_cost, verbose):
    model, service_vars, open_vars = base_model(open_cost, service_cost, verbose)
    clients = len(service_cost)
    plants = len(open_cost)
    model.addConstrs(
        service_vars[i, j] <= open_vars[j]
        for i in range(clients)
        for j in range(plants)
    )

    return model, service_vars, open_vars


def print_result(open_vars, service_vars):
    print("Open Plants:")
    for k, v in open_vars.items():
        if v.x:
            print(k)
    print("Served Customer:")
    for k, v in service_vars.items():
        if v.x:
            print(k)


def check_result(int_model, lp_model):
    int_vars = int_model.getVars()
    collect = {}
    for var in int_vars:
        collect[var.VarName] = var.X

    lp_vars = lp_model.getVars()
    for var in lp_vars:
        if collect[var.VarName] != var.X:
            return False
    return True


def open_all(open_vars):
    count = 0
    for var in open_vars.values():
        count += var.x
    return count == len(open_vars)



def run_model(callback, name, open_cost, service_cost, quiet, verbose):
    model, service_vars, open_vars = callback(open_cost, service_cost, verbose)
    model.update()
    lp_model = model.relax()
    if verbose:
        print("Run INTEGER model")
    model.optimize()
    if verbose:
        print("Run LINEAR model")
    lp_model.optimize()
    delta = model.objVal - lp_model.objVal
    print(f"{name} INT={model.objVal}, LP={lp_model.objVal}, GAP={delta}")

    if check_result(model, lp_model):
        print("INT Check: pass")
    else:
        print("INT Check: fail")

    if open_all(open_vars):
        print("All Plants are open")
    else:
        print("Some Plants are NOT open")

    if not quiet:
        print_result(open_vars, service_vars)

def parse_arg():
    parser = ArgumentParser()

    parser.add_argument(
        "-p", "--plants", type=int, default=10, help="maximum number of plants to open"
    )
    parser.add_argument(
        "-c", "--customers", type=int, default=100, help="customers to serve"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Do not show open plants and plant-customer relation",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="enable Guorbi console log",
    )
    parser.add_argument(
        "-w",
        "--wait",
        default=False,
        action="store_true",
        help="wait between Model A and Model B execution",
    )

    parser.add_argument(
        "-x", "--sizex", type=int, default=1000, help="set random map width"
    )
    parser.add_argument(
        "-y", "--sizey", type=int, default=1000, help="set random map height"
    )

    parser.add_argument(
        "-r",
        "--random",
        default=False,
        action="store_true",
        help="create a pure random instance",
    )

    parser.add_argument('-o', '--output', help="save instance to given file")

    return parser.parse_args()


def main():

    args = parse_arg()

    if args.random:
        open_cost, service_cost = random_instance(args.plants, args.customers)
    else:
        open_cost, service_cost = random_map(
            args.plants, args.customers, args.sizex, args.sizey
        )

    run_model(model_a, "Model A:", open_cost, service_cost, args.quiet, args.verbose)
    print()
    if args.wait:
        input("Press enter to continue...")
    print()
    run_model(model_b, "Model B:", open_cost, service_cost, args.quiet, args.verbose)
    if args.output:
        store = {
            'open_cost': open_cost,
            'service_cost': service_cost
        }
        with open(args.output, "w") as out:
            dump(store, out)


if __name__ == "__main__":
    main()
