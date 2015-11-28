
type Argument
    name::AbstractString
    argumenttype::AbstractString
    value::AbstractString
end


type Signature
    positionalarguments::Vector{Argument}
    optionalarguments::Vector{Argument}
    keywordarguments::Vector{Argument}
    varargsname::AbstractString
    kwvarargsname::AbstractString
end

type Function
    name::AbstractString
    modulename::AbstractString
    templateparameters::Vector{AbstractString}
    signature::Signature
    docstring::AbstractString
end

type Field
    name::AbstractString
    fieldtype::AbstractString
    value::AbstractString
end

type AbstractType
    name::AbstractString
    templateparameters::Vector{AbstractString}
    parenttype::AbstractString
    docstring::AbstractString
end

type CompositeType
    name::AbstractString
    templateparameters::Vector{AbstractString}
    parenttype::AbstractString
    fields::Vector{Field}
    constructors::Vector{Function}
    docstring::AbstractString
end

type Module
    name::AbstractString
    modules::Vector{Module}
    abstracttypes::Vector{AbstractType}
    compositetypes::Vector{CompositeType}
    functions::Vector{Function}
    docstring::AbstractString
end

