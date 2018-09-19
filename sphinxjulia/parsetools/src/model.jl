@static if VERSION < v"0.7.0"
  const Nothing = Void
end

abstract type JuliaModel end

mutable struct Argument <: JuliaModel
    name::AbstractString
    argumenttype::AbstractString
    value::AbstractString
end

mutable struct Signature<: JuliaModel
    positionalarguments::Vector{Argument}
    optionalarguments::Vector{Argument}
    keywordarguments::Vector{Argument}
    varargs::Union{Argument, Nothing}
    kwvarargs::Union{Argument, Nothing}
end

mutable struct Function<: JuliaModel
    name::AbstractString
    modulename::AbstractString
    templateparameters::Vector{AbstractString}
    signature::Signature
    docstring::AbstractString
end

mutable struct Field<: JuliaModel
    name::AbstractString
    fieldtype::AbstractString
    value::AbstractString
end

mutable struct Abstract<: JuliaModel
    name::AbstractString
    templateparameters::Vector{AbstractString}
    parenttype::AbstractString
    docstring::AbstractString
end

mutable struct CompositeType<: JuliaModel
    name::AbstractString
    templateparameters::Vector{AbstractString}
    parenttype::AbstractString
    fields::Vector{Field}
    constructors::Vector{Function}
    docstring::AbstractString
end

mutable struct Module<: JuliaModel
    name::AbstractString
    body::Vector{Union{Module,Abstract,CompositeType,Function}}
    docstring::AbstractString
end

