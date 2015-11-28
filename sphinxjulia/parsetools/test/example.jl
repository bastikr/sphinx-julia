module mymodule

"""
This is an inner module.
"""
module submodule
    innerfunction(x) = 1
end

f(x) = 2

"""
This is my abstract type.
"""
abstract MyAbstractType

"""
And a real type.
"""
type MyType

    """
    This is a.
    """
    # a::Int
    b::Int = 1

    """
    Constructor
    """
    MyType(x,y) = MyTypes(x)

    function MyTypes(x)
        new(x)
    end
end

function f(args...; kwargs...)
end

"""
A Function.
"""
function f(x; y=1)
    return x
end

"""
A complex function.
"""
function f{T1<:Int, T2}(a, b::T1, c=3, d::Bool=true, args...; x=1, y::T2="asd", kwargs...)
    return x
end

abstract AnotherAbstractType

end