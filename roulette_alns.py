#! /usr/bin/python  

import random

class Method:
    def __init__(self, function, points):
        self.function = function
        self.points = points


def compute_roulette(methods):
    total = sum((m.points for m in methods))
    for m in methods:
        yield m.points / total


def select_next(methods):
    weights = compute_roulette(methods)
    index, = random.choices(range(len(methods)), weights=weights)
    return methods[index].function


def main():
    methods = [
        Method('method_a', 61),
        Method('method_b', 34),
        Method('method_c', 21),
        Method('method_d', 89)
    ]

    print(select_next(methods))

if __name__ == "__main__":
    main()
