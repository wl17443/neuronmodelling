from LeakyIntegrateAndFireNeuron import *
import multiprocessing as mp
from ScalingTools import *
import numpy as np 
import matplotlib.pyplot as plt
import random as rnd 

# Simulation times 
SIMULATION_TIME = 1
TIME_STEP = 0.25*ms
TOTAL_TIME_STEPS = np.linspace(0, SIMULATION_TIME, int(SIMULATION_TIME/TIME_STEP)+1)

NETWORK_STRUCTURE = [5, 1]
NR_OF_LIAF_NEURONS = np.sum(NETWORK_STRUCTURE)
LIAF_NEURONS = []
NEURON_SPIKE_TRAINS = []
PROCESSES = []

T = 1
dt = 0.25*ms 
t = np.linspace(0,T,int(T/dt)+1)


if __name__ == '__main__':
    # Initialising neurons 
    # TODO find a better way of defining siblings than this bs 
    MOTHER_PROCESS_CONN_ENDS = []

    for i in range(NR_OF_LIAF_NEURONS):
        # Create mother to children processes pipes 
        pa,c = mp.Pipe()
        MOTHER_PROCESS_CONN_ENDS.append(pa)
        # Randomly choose which neurons are excitatory/inhibitory according to a probability (?)
        if rnd.random() >= 0.5:
            ntype = 'i'
        else: ntype = 'e'
        LIAF_NEURONS.append(LeakyIntegrateAndFireNeuron(Id=i, neurontype=ntype, to_siblings_conns=[], from_siblings_conns=[], main_conn=c))
    
    # TODO connect to a random number of next layer neurons determined by user 
    # This ultimately defines how the neurons are connected to each other 
    if len(NETWORK_STRUCTURE) > 1:
        for layer_nr in range(len(NETWORK_STRUCTURE)-1):
            for neuron_nr in range(NETWORK_STRUCTURE[layer_nr]):
                end1, end2 = mp.Pipe()
                LIAF_NEURONS[neuron_nr].to_siblings_conns.append(end1)
                LIAF_NEURONS[(layer_nr+1)*NETWORK_STRUCTURE[layer_nr]].from_siblings_conns.append(end2)
                

    # Manually adding conns for two neurons 
    # end1, end2 = mp.Pipe()
    # LIAF_NEURONS[0].sibling_conns = end1
    # LIAF_NEURONS[1].sibling_conns = end2

    # TODO Create a layer of neurons to a single neuron 

    # Start parallelised neuron processes
    for neuron in LIAF_NEURONS:
        PROCESSES.append(mp.Process(target=neuron.simulate))
    for process in PROCESSES:
        process.start()

    for pa in MOTHER_PROCESS_CONN_ENDS:
        spikeTrain = pa.recv()
        NEURON_SPIKE_TRAINS.append(spikeTrain)
        plt.plot(t, spikeTrain)

    # TODO implement a live spike train presenter (?)
    plt.show()