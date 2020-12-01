using DrWatson
@quickactivate "Ring Attractor"

using DataFrames
using Statistics
include(srcdir("hebb.jl"))
include(srcdir("stability.jl"))

h0 = 5e-7
h1 = 5e-6
n0 = 0.0
n1 = 2e-3
step_h = 5e-8
step_n = 2e-5
seed=2020

r_h = h0:step_h:h1
r_n = n0:step_n:n1

m = noise_vs_hebb(r_h, r_n, seed)
tmp = @dict h0 h1 n0 n1 step_h step_n seed
safesave(datadir("stability", "hebb", savename(tmp, "csv")), m)
