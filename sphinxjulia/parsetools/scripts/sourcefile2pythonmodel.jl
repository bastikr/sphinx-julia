include("../src/parsetools.jl")

@static if VERSION < v"0.7.0"
    stdout = STDOUT
end

sourcepath = ARGS[1]
model = parsetools.reader.read_file(sourcepath)
parsetools.writer.write_python(stdout, model)
