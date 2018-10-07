"""
Symbolic mathematical computation library.
"""

abstract type MathObject end

struct Symbol <: MathObject
    name::AbstractString
end

struct Sum <: MathObject
    args::Vector{Symbol}
end

"""
Add two symbols.

Arguments
---------
a
    First argument.
b
    Second argument.
"""
function add(a::T, b::T) where {T}
    return Sum(Symbol[a, b])
end
