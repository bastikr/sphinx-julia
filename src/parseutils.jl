module parseutils


function write_parameter(f, parameter::Dict)
    name = string(parameter["name"])
    functype = string(get(parameter, "type", ""))
    value = string(get(parameter, "value", ""))
    write(f, "{")
    write(f, "'name' : '$name',")
    write(f, "'type' : '$functype',")
    write(f, "'value' : '$value'")
    write(f, "}")
end


function write_function(f, func::Dict)
    name = string(func["name"])
    templateparameters = [string(x) for x=func["templateparameters"]]
    arguments = func["arguments"]
    kwarguments = func["kwarguments"]
    docstring = func["docstring"]

    write(f, "{")
    write(f, "'name' : '$name',")
    write(f, "'templateparameters' : [")
    for arg=templateparameters
        write(f, "'$arg',")
    end
    write(f, "],")
    write(f, "'arguments' : [")
    for arg=arguments
        write_parameter(f, arg)
        write(f, ",")
    end
    write(f, "],")
    write(f, "'kwarguments' : [")
    for arg=kwarguments
        write_parameter(f, arg)
        write(f, ",")
    end
    write(f, "],")
    write(f, "'docstring' : r'''$docstring'''")
    write(f, "}")

end

function write_functions(f, functions)
    write(f, "[\n    ")
    for func=functions
        write_function(f, func)
        write(f, ",\n    ")
    end
    write(f, "]")
end

function parsefile(sourcepath)
    f = open(sourcepath)
    buf = readall(f)
    close(f)
    state = Dict()
    walk_ast(state, parse(buf))
    return state
end

function get(d::Dict, key, value)
    if !haskey(d, key)
        d[key] = value
    end
    return d[key]
end

function handle_parameter(parameter)
    d = Dict()
    if typeof(parameter) == Symbol
        d["name"] = parameter
    elseif typeof(parameter) == Expr
        if parameter.head == :kw
            keyword = parameter.args[1]
            if typeof(keyword) == Symbol
                d["name"] = keyword
            else
                @assert keyword.head == Symbol("::")
                d["name"] = keyword.args[1]
                d["type"] = keyword.args[2]
            end
            d["value"] = parameter.args[2]
        else
            @assert parameter.head == Symbol("::")
            d["name"] = parameter.args[1]
            d["type"] = parameter.args[2]
        end
    end
    return d
end

function handle_signature(signature)
    d = Dict("params"=>Dict[], "kwparams"=>Dict[])
    for arg=signature
        if typeof(arg)==Expr && arg.head==:parameters
            d["kwparams"] = handle_signature(arg.args)[1]
        else
            push!(d["params"], handle_parameter(arg))
        end
    end
    return d["params"], d["kwparams"]
end

function handle_function(state::Dict, x::Expr)
    funcexpr = x.args[1]
    name = funcexpr.args[1]
    if typeof(name) == Symbol
        templateparameters = Symbol[]
    else
        templateparameters = Symbol[name.args[2:end]...]
        name = name.args[1]
    end
    signature = funcexpr.args[2:end]
    arguments, kwarguments = handle_signature(signature)
    if length(state["nodes"])>1
        parentnode = state["nodes"][end-1]
        if parentnode.head == :macrocall && parentnode.args[1] == symbol("@doc")
            docstring = parentnode.args[2]
        else
            docstring = ""
        end
    else
        docstring = ""
    end
    funcs = get(state, "functions", [])
    d = Dict("name"=>name,
             "templateparameters"=>templateparameters,
             "arguments"=>arguments,
             "kwarguments"=>kwarguments,
             "docstring"=>docstring
            )
    push!(funcs, d)
end

function walk_ast(state::Dict, x::Expr)
    nodes = get(state, "nodes", Expr[])
    push!(nodes, x)

    if x.head == :function
        handle_function(state, x)
    else
        for arg=x.args
            if typeof(arg)==Expr
                walk_ast(state, arg)
            end
        end
    end
    pop!(nodes)
end



end #module