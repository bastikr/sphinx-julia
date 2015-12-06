from docutils import nodes

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
                if isinstance(fieldtype, tuple):
                    fieldtype = fieldtype[0]
                setattr(self, fieldname, fieldtype())
        assert len(kwargs) == 0

    @classmethod
    def from_string(cls, env, text):
        return cls(env, name=text)


class JuliaModelNode(JuliaModel, nodes.Element):

    def __init__(self, **kwargs):
        nodes.Element.__init__(self)
        JuliaModel.__init__(self, **kwargs)

    def uid(self, scope):
        return ".".join(scope + [self.name])

    def register(self, docname, scope, dictionary):
        if self.name in dictionary:
            entries = dictionary[self.name]
        else:
            entries = []
            dictionary[self.name] = entries
        entry = {
            "docname": docname,
            "scope": scope.copy(),
            "uid": self.uid(scope)
        }
        entries.append(entry)


class Argument(JuliaModel):
    __fields__ = {"name":str, "argumenttype": str, "value": str}

    def __str__(self):
        return self.name + "::" + self.argumenttype + "=" + self.value


class Signature(JuliaModel):
    __fields__ = {"positionalarguments": list, "optionalarguments": list,
                  "keywordarguments": list,
                  "varargs": (type(None), Argument),
                  "kwvarargs": (type(None), Argument)}

    def __str__(self):
        l = self.positionalarguments + self.optionalarguments\
            + [self.varargs] + [";"] + self.positionalarguments + [self.kwvarargs]
        return str([str(x) for x in l])


class Function(JuliaModelNode):
    __fields__ = {"name": str, "modulename": str, "templateparameters": list,
                  "signature": Signature, "docstring": str}

    def uid(self, scope):
        x = bytes(str(self.templateparameters) + str(self.signature), "UTF-16")
        name = self.name + "-" + hashlib.md5(x).hexdigest()
        return ".".join(scope + [name])

    def register(self, docname, scope, dictionary):
        if self.name in dictionary:
            entries = dictionary[self.name]
        else:
            entries = []
            dictionary[self.name] = entries
        entry = {
            "docname": docname,
            "scope": scope.copy(),
            "templateparameters": self.templateparameters,
            "signature": self.signature,
            "uid": self.uid(scope),
        }
        entries.append(entry)


class Field(JuliaModel):
    __fields__ = {"name": str, "fieldtype": str, "value": str}


class Type(JuliaModelNode):
    __fields__ = {"name": str, "templateparameters": list, "parenttype": str,
                  "fields": list, "constructors": list, "docstring": str}


CompositeType = Type


class Abstract(JuliaModelNode):
    __fields__ = {"name": str, "templateparameters": list, "parenttype": str,
                  "docstring": str}


class Module(JuliaModelNode):
    __fields__ = {"name": str, "body":list, "docstring": str}

    def __init__(self, **kwargs):
        JuliaModelNode.__init__(self, **kwargs)
        self.extend(self.body)
