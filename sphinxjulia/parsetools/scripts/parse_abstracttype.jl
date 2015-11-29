include("../src/parsetools.jl")

text = ARGS[1]
ast = parse(text)
model = parsetools.reader.read_abstracttype(ast, "")
parsetools.writer.write_python(STDOUT, model)