module parsetools

export model, reader

module model
    include("model.jl")
end

module reader
    export read_file

    include("reader_file.jl")
end

end