module parsetools

module model
    include("model.jl")
end

module reader
    export read_file

    include("reader_file.jl")
end

module writer
    export write_python

    include("writer_python.jl")
end

end # module
