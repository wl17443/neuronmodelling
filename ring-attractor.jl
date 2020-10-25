module RingAttractor

using Distributions
using Random

const ms = 1e-3
const mV = 1e-3
const nF = 1e-9
const dt = 1e-3

const Vₜ = -48 * mV
const Vᵣ = -80 * mV
const Cₘ = 1e-9
const Eᵢ = -70 * mV
const Eₑ = 0.
const Eₘ = -70 * mV
const Eₗ = -70 * mV
const τᵣ = 2 * ms
const τₛ = 5 * ms
const τₘ = 5 * ms
const kₛ = 1/(5 * ms * exp(-1.))
const Eₗₜ = Eₗ/τₛ

const Nₑ = 5
const Nᵢ = 7
const fp_w = 2


mutable struct Ring <: Function
	N::Int32
	time::Int32
	t::Int32

	noise::Float64
	fps::Tuple # TODO take fpn and autogenerate fps
	seed::Int32

	wₑ::Float64
	wᵢ::Float64
	wₑᶠ::Float64
	wᵢᶠ::Float64
	Wₑ::Array{Float64, 2}
	Wᵢ::Array{Float64, 2}


	S::Array{Bool, 2}
	V::Array{Float64, 2}
	Z::Array{Float64, 2}

	Δs::Array{Float64, 2}
	k::Array{Float64, 1}


	function Ring(;N=64, time=10000, noise=5e-4, fps=(), seed=0, wₑ=0.05, wᵢ=0.10, wₑᶠ=0.05, wᵢᶠ=0.25)
		self = new()

		self.N = N
		self.time = time
		self.noise = noise
		self.fps = fps
		self.seed = seed
		if seed != 0
			Random.seed!(seed)
		end

		self.wₑ = wₑ
		self.wᵢ = wᵢ
		self.wₑᶠ = wₑᶠ
		self.wᵢᶠ = wᵢᶠ

		self.Wₑ = zeros(N, N)
		self.Wᵢ = zeros(N, N)
		self.V = zeros(N, time)
		self.Z = zeros(N, time)
		self.S = falses(N, time)
		self.Δs = zeros(N, 3)
		self.k = zeros(N)
		self.t = 0

		init!(self)

		return self
	end
end


function (r::Ring)()
	init!(r)

	for r.t = 1:r.time-1
		idx = r.t % 3 + 1
		r.S[:, r.t] .= view(r.V, :, r.t) .== 0.

		r.k .= @views r.Δs[:, idx] .* exp.(-r.Δs[:, idx] ./ τₛ)

		r.V[:, r.t+1] .= @views r.V[:, r.t] .+ ((Eₗₜ .- r.V[:, r.t] ./ τₘ ) .- (r.V[:, r.t].-Eₑ) .* (r.Wₑ' * r.k) .- (r.V[:, r.t].-Eᵢ) .* (r.Wᵢ' * r.k)) .* dt
		r.V[:, r.t+1] .+= @view r.Z[:, r.t+1]

		r.V[view(r.V,:, r.t) .> Vₜ, r.t+1] .= 0.
		r.V[view(r.S, :, r.t), r.t+1] .= Vᵣ

		r.Δs .+= dt
		r.Δs[view(r.S, :, r.t), idx] .= 0.
	end
end


function setweights!(r::Ring)
	r.Wₑ .= reshape(Float64[min(r.N - abs(i-k), abs(i-k)) for i in 1:r.N for k in 1:r.N], (r.N,r.N))
	r.Wᵢ .= deepcopy(r.Wₑ)

	replace!(x -> 0., view(r.Wₑ, r.Wₑ .> Nₑ))
	replace!(x -> r.wₑ, view(r.Wₑ, r.Wₑ .> 0.))

	replace!(x -> 0., view(r.Wᵢ, Nₑ .>= r.Wᵢ))
	replace!(x -> 0., view(r.Wᵢ, r.Wᵢ .> Nₑ + Nᵢ))
	replace!(x -> r.wᵢ,  view(r.Wᵢ, r.Wᵢ .> 0.))

    for fp in r.fps
		r = (fp:fp + 2) .- 1
		replace!(view(r.Wₑ, r, :), r.wₑ => r.wₑᶠ)
		replace!(view(r.Wᵢ, r, :), r.wᵢ => r.wᵢᶠ)
    end

	r.Wₑ .*= kₛ * 1e-6 / Cₘ
	r.Wᵢ .*= kₛ * 1e-6 / Cₘ
end

function init!(r::Ring)
	r.Δs = fill(0.2, r.N, 3)
	r.Z = rand(Normal(0., r.noise), r.N, r.time)
	replace!(view(r.V, :, 1), 0. => Vᵣ)
	replace!(view(r.V, (r.N÷2:r.N÷2+5).-2, 1), Vᵣ => 0.)
	setweights!(r)
end

export Ring

end
