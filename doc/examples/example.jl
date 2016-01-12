"""
Symbolic mathematical computation library.
"""

abstract MathObject

type Symbol <: MathObject
    name::AbstractString
end

type Sum <: MathObject
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
function add{T}(a::T, b::T)
    return Sum(Symbol[a, b])
end
