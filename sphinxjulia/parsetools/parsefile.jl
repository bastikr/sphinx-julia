include("parseutils.jl")
using ArgParse
using parseutils

s = ArgParseSettings()

@add_arg_table s begin
    "sourcepath"
        required = true
    "targetpath"
        required = false
end

parsed_args = parse_args(s)

sourcepath = parsed_args["sourcepath"]
targetpath = parsed_args["targetpath"]

state = parseutils.parsefile(sourcepath)

if targetpath==nothing
    f = STDOUT
else
    f = open(targetpath, "w")
end

parseutils.write_functions(f, state["functions"])
close(f)
