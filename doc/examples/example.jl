# examples/example.jl
"""
Solve all the things.

Arguments
---------
a
    Very important parameter.
b
    Not so important parameter

Keyword Arguments
-----------------
state
    It's a trap.
flag
    Do. Or do not. There is no try.
"""
function myfunc{T}(a::T, b=1; state="Foo", flag::Boolean=True, kwargs...)
    # Do stuff
    return a + b + state + flag + kwargs
end