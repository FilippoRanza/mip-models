#! /usr/bin/python

import numpy as np
from matplotlib import pyplot as plt

def cooling_values(base_temperature, alfa):
    while base_temperature > 1:
        yield base_temperature
        base_temperature *= alfa

def plot_probability(degratation, temperature):
    tmp = -(degratation / temperature)
    prob = np.exp(tmp)
    plt.plot(prob)

def main():
    degradation = np.linspace(0, 100)
    legend = []
    for t in cooling_values(100, 0.5):
        plot_probability(degradation, t)
        legend.append(f"T: {t}")
    
    plt.legend(legend)
    plt.show()



if __name__ == "__main__":

    main()


