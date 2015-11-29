include("../src/parsetools.jl")

# m = parsetools.reader.read_file("../src/model.jl")

# f = open("t.py", "w")
# parsetools.writer.write_python(f, m)
# close(f)

# m = parsetools.reader.read_file("../src/reader_file.jl")
m = parsetools.reader.read_file("example2.jl")
println(m)
# m = parsetools.reader.read_file("/usr/share/julia/base/abstractarray.jl")

# f = open("t.py", "w")
# parsetools.writer.write_python(f, m)
# close(f)