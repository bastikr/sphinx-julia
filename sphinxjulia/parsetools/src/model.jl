abstract JuliaModel

type Argument <: JuliaModel
    name::AbstractString
    argumenttype::AbstractString
    value::AbstractString
end

type Signature<: JuliaModel
    positionalarguments::Vector{Argument}
    optionalarguments::Vector{Argument}
    keywordarguments::Vector{Argument}
    varargsname::AbstractString
    kwvarargsname::AbstractString
end

type Function<: JuliaModel
    name::AbstractString
    modulename::AbstractString
    templateparameters::Vector{AbstractString}
    signature::Signature
    docstring::AbstractString
end

type Field<: JuliaModel
    name::AbstractString
    fieldtype::AbstractString
    value::AbstractString
end

type AbstractType<: JuliaModel
    name::AbstractString
    templateparameters::Vector{AbstractString}
    parenttype::AbstractString
    docstring::AbstractString
end

type CompositeType<: JuliaModel
    name::AbstractString
    templateparameters::Vector{AbstractString}
    parenttype::AbstractString
    fields::Vector{Field}
    constructors::Vector{Function}
    docstring::AbstractString
end

type Module<: JuliaModel
    name::AbstractString
    body::Vector{Union{Module,AbstractType,CompositeType,Function}}
    docstring::AbstractString
end

