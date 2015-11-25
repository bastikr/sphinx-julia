.. autodoc-julia documentation master file, created by
   sphinx-quickstart on Mon Nov 23 11:00:45 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to autodoc-julia's documentation!
=========================================

.. jl:class:: Float64

.. function:: ode{T}(F::Function, tspan::Vector{Float64}, x0::Vector{T}; fout::Union{Function, Void} = nothing,

    :param Float64 reltol: Relative tolerance
    :param Float64 abstol: Absolute tolerance
..              reltol::Float64 = 1.0e-6,

                h0::Float64 = NaN,
                hmin::Float64 = (tspan[end]-tspan[1])/1e9,
                hmax::Float64 = (tspan[end]-tspan[1]),
                display_initialvalue::Bool = true,
                display_intermediatesteps::Bool = false,
                )

.. py:function:: f(arg, x=1)

.. jl:function:: ode(F::Function, tspan::Vector{Float64}, x0::Vector{T}; fout::Union{Function, Void} = nothing, reltol=1e-6)

    :param Float64 reltol: Relative tolerance

.. jl:autofunction:: ../src/DormandPrince45.jl ode

.. jl:autofunction:: ../src/DormandPrince45.jl interpolate

.. jl:autofunction:: ../src/DormandPrince45.jl error_estimate


Indices and tables
==================


