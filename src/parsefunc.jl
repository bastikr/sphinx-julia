include("parseutils.jl")
using ArgParse
using parseutils

s = ArgParseSettings()

@add_arg_table s begin
    "functionstring"
        required = true
    "targetpath"
        required = false
end

parsed_args = parse_args(s)

functionstring = parsed_args["functionstring"]
targetpath = parsed_args["targetpath"]

state = Dict()
parseutils.walk_ast(state, parse(functionstring))

if targetpath==nothing
    f = STDOUT
else
    f = open(targetpath, "w")
end

parseutils.write_function(f, state["functions"][1])