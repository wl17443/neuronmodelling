import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from connect import connect_with_fixed_points
from lif_model import LIF

time = 300
n = 100
weights = [0.06, 0.10, 0.06, 0.15] # inh weight, exc weight, fixed point inh, fixed point exc
dt = 1
spike_source = [c for c in range(40, 41)]
# spike_source2 = [c for c in range(70,80)]

neurons = [LIF(ID, dt=dt, noise_mean=1e-11, noise_std=5e-10) for ID in range(n)]


connect_with_fixed_points(neurons, n, weights)



potentials = [[] for _ in range(n)]
for t in range(time):
    for neuron in neurons:

        if neuron.id in spike_source:
            neuron.exc_ps_td.append((t * 1e-3, weights[0]))

# if t > 100:
        #     if neuron.id in spike_source2:
        #         for _ in range(5):
        #             neuron.exc_ps_td.append(((t - 100) *  1e-3, ew))
        
        # if t > 200:
        #     if neuron.id in spike_source:
        #         for _ in range(5):
        #             neuron.exc_ps_td.append(((t - 200) * 1e-3, ew))


        neuron.step()

        potentials[neuron.id].append(neuron.V)


# Plots
fig = plt.figure(figsize=(10,10))

df = pd.DataFrame(potentials)
sns.heatmap(df, vmin=-0.08, vmax=0.0, cmap="viridis", xticklabels=int(time/10), yticklabels=5, cbar_kws={'label':"Membrane Potential (V)"})
plt.xlabel("Time (ms)")
plt.ylabel("# of neuron")
plt.subplots_adjust(left=0.07, bottom=0.07, right=0.97, top=0.95)

plt.show()

