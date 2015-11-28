include("../src/parsetools.jl")

sourcepath = ARGS[1]
model = parsetools.reader.read_file(sourcepath)
parsetools.writer.write_python(STDOUT, model)
