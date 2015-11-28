using quantumoptics

# Module level
n = names(quantumoptics)


# Type level
fieldnames(quantumoptics.FockBasis)
parameters = quantumoptics.FockBasis.parameters
name = quantumoptics.FockBasis.name
types = quantumoptics.FockBasis.types
isabstract = quantumoptics.FockBasis.abstract
super = quantumoptics.FockBasis.super
constructors = methods(quantumoptics.FockBasis)

# Methods
miter = methods(quantumoptics.tensor)
modulename = miter.module
mvec = collect(miter)
m = mvec[3]
parameters = m.sig.parameters
templatevars = m.tvars

# println(parameters)
# println(templatevars)

miter = methods(quantumoptics.timeevolution.master)
modulename = miter.module
mvec = collect(miter)
m = mvec[3]
parameters = m.sig.parameters
templatevars = m.tvars

# println(m)
# println(parameters)
# println(templatevars)

f(x; graz=6) = y

println(fieldnames(name))
println(typeof(name.module))

# Base.Meta.dump(mvec[1].sig.keywords)
# miter = methods(f)
# println(length(miter))
# m = first(miter)
# println(fieldnames(m))
# println(fieldnames(miter.kwsorter))
# println(fieldnames(miter.kwsorter.env))
# println(miter.kwsorter)

# li = m.func.code
# e = Base.uncompressed_ast(li)
# argnames = e.args[1]
# println(argnames)
# s = symbol("?")
# decls = [Base.argtype_decl(get(argnames,i,s), m.sig.parameters[i]) for i=1:Base.length(m.sig.parameters)]
# shift!(decls)
# kwargs = filter!(x->!('#' in string(x)), e.args[2][1])
# println(kwargs)

# println(e.args)

