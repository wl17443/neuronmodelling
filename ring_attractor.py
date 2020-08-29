from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import circular_mean
from lif_model import LIF


class RingAttractor:
    "A self-contained class for the ring attractor"

    def __init__(self,
                 n=128,
                 noise=2.0e-3,
                 # TODO: pick more stable fixed point weights
                 weights=(0.050, 0.088, 0.050, 0.15),
                 fixed_points_number=0, 
                 time=300,
                 plot=False):

        self.n = n
        self.noise = noise
        self.weights = weights
        self.fp_n = fixed_points_number
        self.time = time
        self.plot = plot

        self.neurons = [LIF(ID=i, angle=360.0/n*i, noise_mean=0, noise_std=self.noise,)
                        for i in range(n)]

        # TODO: move weights, fp_n and noise to the simulate method
        self.fixed_points = self.get_fixed_points()

        self.connect_with_fixed_points()

    def simulate(self):

        mid_point = self.get_mid_point()

        potentials = [[] for _ in range(self.n)]
        for t in range(self.time):
            for neuron in self.neurons:

                self.input_source(mid_point=mid_point, n_of_spikes=5,
                                  weight=self.weights[0], begin_time=0, neuron=neuron, time=t)
                neuron.step()
                potentials[neuron.id].append(neuron.V)

        df, e = self.compute_gain(potentials, mid_point)

        if self.plot:
            self.plot_potentials(df, e)

        return e

    def input_source(self, mid_point, n_of_spikes, weight, begin_time, neuron, time):
        sources = [i for i in range(mid_point - 2, mid_point + 3)]

        if time > begin_time:
            if neuron.id in sources:
                for _ in range(n_of_spikes):
                    neuron.exc_ps_td.append(
                        ((time - begin_time) * 1e-3, weight))

    def connect_with_fixed_points(self):
        for neur in self.neurons:
            if neur.id in self.fixed_points:
                for i in range(5, 12):
                    neur.synapses["inh"][self.neurons[(
                        neur.id + i) % self.n]] = self.weights[3]
                    neur.synapses["inh"][self.neurons[neur.id - i]
                                         ] = self.weights[3]
                for i in range(1, 5):
                    neur.synapses["exc"][self.neurons[(
                        neur.id + i) % self.n]] = self.weights[2]
                    neur.synapses["exc"][self.neurons[neur.id - i]
                                         ] = self.weights[2]

            else:
                for i in range(5, 12):
                    neur.synapses["inh"][self.neurons[(
                        neur.id + i) % self.n]] = self.weights[1]
                    neur.synapses["inh"][self.neurons[neur.id - i]
                                         ] = self.weights[1]
                for i in range(1, 5):
                    neur.synapses["exc"][self.neurons[(
                        neur.id + i) % self.n]] = self.weights[0]
                    neur.synapses["exc"][self.neurons[neur.id - i]
                                         ] = self.weights[0]

    def get_fixed_points(self):
        if self.fp_n == 0:
            return []

        index = np.arange(self.n)
        interval = self.n // self.fp_n

        distances = index % interval
        return np.where(distances < 3)[0]

    def get_mid_point(self):
        if self.fp_n <= 1:
            return self.n // 2


        free_points = set(np.arange(self.n)) - set(self.fixed_points)
        median = [*free_points][len(free_points) // 4]


        high = self.fixed_points[self.fixed_points > median][0]
        low = self.fixed_points[self.fixed_points < median][-1]
        mid_point = (high + low) // 2

        return mid_point

    def compute_gain(self, potentials, mid_point):
        df = pd.DataFrame(potentials)
        df.index = [self.neurons[i].angle for i in df.index]
        spikes = df == 0.0

        # sparse = spikes.astype(pd.SparseDtype())
        # coo = sparse.sparse.to_coo()
        # coo.eliminate_zeros()

        # regr = LinearRegression(fit_intercept=True)
        
        # x = coo.col.reshape(-1, 1)
        # y = coo.row.reshape(-1, 1)

        # regr.fit(x, y)
        # error = np.abs(regr.coef_[0][0])

        

        spikes = spikes.iloc[:, -30:]
        spikes = spikes.astype(int)
        spikes = spikes.apply(lambda x: x * x.index)
        spikes = spikes.replace(0, np.nan)

        means = spikes.apply(circular_mean)
        total_mean = circular_mean(means)
        error = np.abs(self.neurons[mid_point].angle - total_mean)

        print("total_mean", total_mean)
        print(self.neurons[mid_point].angle)

        return df, error


    def plot_potentials(self, df, error):
        _, ax = plt.subplots(figsize=(10, 10))
        sns.heatmap(df, vmin=-0.08, vmax=0.0, cmap="viridis", xticklabels=int(self.time/10),
                    yticklabels=5, cbar_kws={'label': "Membrane Potential (V)"}, ax=ax)
        plt.xlabel("Time (ms)")
        plt.ylabel("Orientation of neuron")
        plt.subplots_adjust(left=0.07, bottom=0.07, right=0.97, top=0.89)

        labels = [item.get_text() for item in ax.get_yticklabels()]

        # for i, l in enumerate(labels):
        #     if int(l) in fixed_points:
        #         labels[i] = labels[i] + '\nFP'

        ax.set_yticklabels(labels)

        ax.set_title("Number of fixed points: {}\nNoise: {:.3e}\nWeights: {}\nError: {:.3f}".format(
            self.fp_n, self.noise, self.weights, error * self.time))

        plt.savefig(
            f"images/{datetime.now().strftime('%d-%m-%Y, %H:%M:%S')}.png")
        plt.show()

if __name__ == "__main__":

    # np.random.seed(42)
    ring = RingAttractor(n=64, noise=3e-3, weights=(0.050, 0.100, 0.050, 0.250), fixed_points_number=2, time=100, plot=True)
    error = ring.simulate()
