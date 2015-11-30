from docutils import nodes


class JuliaModel:
    __fields__ = None

    def __init__(self, **kwargs):
        for fieldname in self.__fields__:
            setattr(self, fieldname, kwargs.pop(fieldname))

        assert len(kwargs) == 0


class JuliaModelNode(JuliaModel, nodes.Admonition, nodes.Element):

    def __init__(self, **kwargs):
        JuliaModel.__init__(self, **kwargs)
        nodes.Admonition.__init__(self)
        nodes.Element.__init__(self)


class Module(JuliaModelNode):
    orderedobjects = None
    __fields__ = ("name", "modules", "abstracttypes", "compositetypes", "functions", "docstring")


class CompositeType(JuliaModelNode):
    __fields__ = ("name", "templateparameters", "parenttype", "fields", "constructors", "docstring")


class AbstractType(JuliaModelNode):
    __fields__ = ("name", "templateparameters", "parenttype", "docstring")


class Function(JuliaModelNode):
    __fields__ = ("name", "modulename", "templateparameters", "signature", "docstring")


class Field(JuliaModel):
    __fields__ = ("name", "fieldtype", "value")


class Signature(JuliaModel):
    __fields__ = ("positionalarguments", "optionalarguments", "keywordarguments", "varargsname", "kwvarargsname")


class Argument(JuliaModel):
    __fields__ = ("name", "argumenttype", "value")
