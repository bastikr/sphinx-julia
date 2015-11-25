sourcepath = "../test/src/DormandPrince45.jl"
targetpath = "t.ast"

function save(targetpath, functions)
    f = open(targetpath, "w")
    write(f, "[\n")
    for func=functions
        name = func["name"]
        templateparameters = func["templateparameters"]
        doc = func["doc"]
        write("{$name")
    end
end

function parsefile(sourcepath)
    f = open(sourcepath)
    buf = readall(f)
    close(f)
    state = Dict()
    walk_ast(state, parse(buf))
end

function get(d::Dict, key, value)
    if !(key in keys(d))
        d[key] = value
    end
    return d[key]
end

function parseparameter(parameter)
    d = Dict()
    if typeof(parameter) == Symbol
        d["name"] = parameter
    elseif typeof(parameter) == Expr
        println(parameter)
        d["name"] = parameter.args[1]
    end
    return d
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
    println("Parameters:")
    parameters = [parseparameter(arg) for arg=funcexpr.args[2:end]]
    parentnode = state["nodes"][end-1]
    if parentnode.head == :macrocall && parentnode.args[1] == symbol("@doc")
        docstring = parentnode.args[2]
    else
        docstring = ""
    end
    funcs = get(state, "functions", [])
    d = Dict("name"=>name,
             "templateparameters"=>templateparameters,
             "docstring"=>docstring)
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

parsefile(sourcepath)
