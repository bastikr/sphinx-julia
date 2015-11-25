using ArgParse

s = ArgParseSettings()

@add_arg_table s begin
    "sourcepath"
        required = true
    "targetpath"
        required = true
end

parsed_args = parse_args(s)

sourcepath = parsed_args["sourcepath"]
targetpath = parsed_args["targetpath"]

# sourcepath = "../test/src/DormandPrince45.jl"
# targetpath = "t.py"

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

function save(targetpath, functions)
    f = open(targetpath, "w")
    write(f, "[\n    ")
    for func=functions
        write_function(f, func)
        write(f, ",\n    ")
    end
    write(f, "]")
    close(f)
end

t = """
function f{T,H}(a, b::Float64, c=1, d::Int=2; e=[1, 2], f::T=2)
    return a::H
end
"""

function parsefile(sourcepath, targetpath)
    f = open(sourcepath)
    buf = readall(f)
    close(f)
    state = Dict()
    walk_ast(state, parse(buf))
    save(targetpath, state["functions"])
end

function get(d::Dict, key, value)
    # if !(key in keys(d))
    if !haskey(d, key)
        d[key] = value
    end
    return d[key]
end

function parseparameter(parameter)
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

function parsesignature(signature)
    d = Dict("params"=>Dict[], "kwparams"=>Dict[])
    for arg=signature
        if typeof(arg)==Expr && arg.head==:parameters
            d["kwparams"] = parsesignature(arg.args)[1]
        else
            push!(d["params"], parseparameter(arg))
        end
    end
    return d["params"], d["kwparams"]
end

function parsefunction(state::Dict, x::Expr)
    funcexpr = x.args[1]
    name = funcexpr.args[1]
    if typeof(name) == Symbol
        templateparameters = Symbol[]
    else
        templateparameters = Symbol[name.args[2:end]...]
        name = name.args[1]
    end
    signature = funcexpr.args[2:end]
    arguments, kwarguments = parsesignature(signature)
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
        parsefunction(state, x)
    else
        for arg=x.args
            if typeof(arg)==Expr
                walk_ast(state, arg)
            end
        end
    end
    pop!(nodes)
end

parsefile(sourcepath, targetpath)