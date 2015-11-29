include("../src/parsetools.jl")

text = ARGS[1]
ast = parse(text)
model = parsetools.reader.read_function(ast, "")
parsetools.writer.write_python(STDOUT, model)