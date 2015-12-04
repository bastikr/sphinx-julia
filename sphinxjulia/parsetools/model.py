from docutils import nodes
from docutils.statemachine import ViewList

import hashlib


class JuliaModel:
    __fields__ = None

    def __init__(self, **kwargs):
        for fieldname, fieldtype in self.__fields__.items():
            if fieldname in kwargs:
                arg = kwargs.pop(fieldname)
                assert isinstance(arg, fieldtype)
                setattr(self, fieldname, arg)
            else:
                setattr(self, fieldname, fieldtype())
        assert len(kwargs) == 0

    @classmethod
    def from_string(cls, env, text):
        return cls(env, name=text)


class JuliaModelNode(JuliaModel, nodes.Element):

    def __init__(self, env, **kwargs):
        JuliaModel.__init__(self, **kwargs)
        nodes.Element.__init__(self)
        self["ids"] = [self.uid(env)]
        self.register(env)

    def uid(self, env):
         return ".".join(env.ref_context['jl:scope'] + [self.name])

    def register(self, env):
        typeidentifier = self.__class__.__name__.lower()
        d = env.domaindata['jl'][typeidentifier]
        if self.name in d:
            entries = d[self.name]
        else:
            entries = []
            d[self.name] = entries
        entry = {
            "docname": env.docname,
            "scope": env.ref_context['jl:scope'].copy(),
            "uid": self["ids"][0]
        }
        entries.append(entry)


class Argument(JuliaModel):
    __fields__ = {"name":str, "argumenttype": str, "value": str}


class Signature(JuliaModel):
    __fields__ = {"positionalarguments": list, "optionalarguments": list,
                  "keywordarguments": list,
                  "varargsname": Argument, "kwvarargsname": Argument}


class Function(JuliaModelNode):
    __fields__ = {"name": str, "modulename": str, "templateparameters": list,
                  "signature": Signature, "docstring": str}
    hashfunc = hashlib.md5()

    def uid(self, env):
        scope = env.ref_context['jl:scope']
        x = bytes(str(self.templateparameters) + str(self.signature), "UTF-16")
        self.hashfunc.update(x)
        name = self.name + "-" + self.hashfunc.hexdigest()
        return ".".join(env.ref_context['jl:scope'] + [name])

    def register(self, env):
        typeidentifier = self.__class__.__name__.lower()
        d = env.domaindata['jl'][typeidentifier]
        if self.name in d:
            entries = d[self.name]
        else:
            entries = []
            d[self.name] = entries
        entry = {
            "docname": env.docname,
            "scope": env.ref_context['jl:scope'].copy(),
            "templateparameters": self.templateparameters,
            "signature": self.signature,
            "uid": self["ids"][0]
        }
        entries.append(entry)


class Field(JuliaModel):
    __fields__ = {"name": str, "fieldtype": str, "value": str}


class Type(JuliaModelNode):
    __fields__ = {"name": str, "templateparameters": list, "parenttype": str,
                  "fields": list, "constructors": list, "docstring": str}


class Abstract(JuliaModelNode):
    __fields__ = {"name": str, "templateparameters": list, "parenttype": str,
                  "docstring": str}


class Module(JuliaModelNode):
    __fields__ = {"name": str, "body":str, "docstring": str}
