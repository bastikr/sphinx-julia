using ..model


function Base.string(m::model.JuliaModel)
    typename = last(split(string(typeof(m)), "."))
    d = AbstractString["$(typename)("]
    for name in fieldnames(m)
        p = getfield(m, name)
        if typeof(p) <: AbstractString
            p = repr(p)
        elseif typeof(p) <: Array{AbstractString, 1}
            p = "["*join([repr(x) for x=p], ", ")*"]"
        elseif typeof(p) <: Array
            p = "["*join([string(x) for x=p], ", ")*"]"
        elseif p == nothing
            p = "None"
        else
            p = string(p)
        end
        push!(d, "$name=$p, ")
    end
    push!(d, ")\n")
    return join(d)
end


function write_python(f, m::model.JuliaModel)
    write(f, string(m))
end
