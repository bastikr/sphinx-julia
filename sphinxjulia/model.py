from __future__ import unicode_literals

from docutils import nodes

import hashlib

try:
    str = unicode
except:
    pass

class JuliaModel:
    __fields__ = None

    def __init__(self, **kwargs):
        for fieldname, fieldtype in self.__fields__.items():
            if fieldname in kwargs:
                arg = kwargs.pop(fieldname)
                if not isinstance(arg, fieldtype):
                    raise ValueError("argtype: {}; fieldtype: {}".format(
                                     type(arg), fieldtype))
                setattr(self, fieldname, arg)
            else:
                if isinstance(fieldtype, tuple):
                    setattr(self, fieldname, None)
                else:
                    setattr(self, fieldname, fieldtype())
        assert len(kwargs) == 0

    @classmethod
    def from_string(cls, env, text):
        return cls(env, name=text)

    def deepcopy(self):
        kwargs = {}
        for fieldname in self.__fields__:
            attr = getattr(self, fieldname)
            if hasattr(attr, "deepcopy"):
                kwargs[fieldname] = attr.deepcopy()
            else:
                kwargs[fieldname] = attr
        return self.__class__(**kwargs)


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
            "scope": list(scope),
            "uid": self.uid(scope)
        }
        entries.append(entry)

    def deepcopy(self):
        obj = JuliaModel.deepcopy(self)
        obj["ids"] = list(self["ids"])
        obj.children = [c for c in self.children]
        #obj.parent = self.parent
        return obj


class Argument(JuliaModel):
    __fields__ = {"name":str, "argumenttype": str, "value": str, "macrocall": str}

    def __str__(self):
        return self.name + "::" + self.argumenttype + "=" + self.value


class Signature(JuliaModel):
    __fields__ = {"positionalarguments": list, "optionalarguments": list,
                  "keywordarguments": list,
                  "varargs": (type(None), Argument,),
                  "kwvarargs": (type(None), Argument,)}

    def __str__(self):
        l = self.positionalarguments + self.optionalarguments\
            + [self.varargs] + [";"] + self.keywordarguments + [self.kwvarargs]
        return str([str(x) for x in l])


class Function(JuliaModelNode):
    __fields__ = {"name": str, "modulename": str, "templateparameters": list,
                  "signature": Signature, "returntype": str, "docstring": str}

    def uid(self, scope):
        # The bytecode will be different for python2 and python3 but that's
        # probably not a problem.
        x = (str(self.templateparameters) + str(self.signature)).encode("UTF-16")
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
            "scope": list(scope),
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

    def __init__(self, **kwargs):
        JuliaModelNode.__init__(self, **kwargs)
        self.extend(self.constructors)


CompositeType = Type


class Abstract(JuliaModelNode):
    __fields__ = {"name": str, "templateparameters": list, "parenttype": str,
                  "docstring": str}


class Module(JuliaModelNode):
    __fields__ = {"name": str, "body":list, "docstring": str}

    def __init__(self, **kwargs):
        JuliaModelNode.__init__(self, **kwargs)
        self.extend(self.body)
