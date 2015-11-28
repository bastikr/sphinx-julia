include("../src/parsetools.jl")

# m = parsetools.reader.read_file("example.jl")
srcdir = "/usr/share/julia/base"

function testdir(sourcedir)
    for name in readdir(sourcedir)
        p = joinpath(sourcedir, name)
        if isfile(p) && endswith(name, ".jl")
            try
                parsetools.reader.read_file(p)
            catch e
                println(p)
                println("==========================")
                println(e)
                println()
            end
        elseif isdir(p)
            testdir(p)
        end
    end
end

testdir(srcdir)
