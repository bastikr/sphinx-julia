from docutils import nodes

class JuliaModel(nodes.General, nodes.Element):
    __fields__ = None

    def __init__(self, **kwargs):
        for fieldname in self.__fields__:
            setattr(self, fieldname, kwargs.pop(fieldname))
        nodes.General.__init__(self)
        nodes.Element.__init__(self)
        assert len(kwargs) == 0

class Module(JuliaModel):
    orderedobjects = None
    __fields__ = ("name", "modules", "abstracttypes", "compositetypes", "functions", "docstring")


class CompositeType(JuliaModel):
    __fields__ = ("name", "templateparameters", "parenttype", "fields", "constructors", "docstring")


class AbstractType(JuliaModel):
    __fields__ = ("name", "templateparameters", "parenttype", "docstring")


class Field(JuliaModel):
    __fields__ = ("name", "fieldtype", "value")


class Function(JuliaModel):
    __fields__ = ("name", "modulename", "templateparameters", "signature", "docstring")


class Signature(JuliaModel):
    __fields__ = ("positionalarguments", "optionalarguments", "keywordarguments", "varargsname", "kwvarargsname")


class Argument(JuliaModel):
    __fields__ = ("name", "argumenttype", "value")
