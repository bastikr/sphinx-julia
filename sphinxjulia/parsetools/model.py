from docutils import nodes
from docutils.statemachine import ViewList

import sphinx


class JuliaModel:
    __fields__ = None

    def __init__(self, **kwargs):
        for fieldname in self.__fields__:
            setattr(self, fieldname, kwargs.pop(fieldname))
        assert len(kwargs) == 0


class JuliaModelNode(JuliaModel, nodes.Element):

    def __init__(self, **kwargs):
        JuliaModel.__init__(self, **kwargs)
        nodes.Element.__init__(self)

    def subnodes(self, directive):
        return []

    def create_node(self, directive):
        self.append(self.parsedocstring(directive))
        self.extend(self.subnodes(directive))
        return self

    def parsedocstring(self, directive):
        classname = self.__class__.__name__
        docstringlines = self.docstring.split("\n")
        directive.env.app.emit('autodoc-process-docstring',
                               classname, self.name, None, {}, docstringlines)
        content = ViewList(docstringlines)
        docstringnode = nodes.paragraph()
        directive.state.nested_parse(content, directive.content_offset,
                                     docstringnode)
        return docstringnode


class Module(JuliaModelNode):
    __fields__ = ("name", "body", "docstring")

    def subnodes(self, directive):
        l = []
        for n in self.body:
            l.append(n.create_node(directive))
        return l

    def match(self, pattern, objtype):
        l = []
        if isinstance(self, objtype) and pattern == self.name:
            l.append(self)
        for obj in self.body:
                l.extend(obj.match(pattern, objtype))
        return l


class CompositeType(JuliaModelNode):
    __fields__ = ("name", "templateparameters", "parenttype", "fields", "constructors", "docstring")

    def match(self, pattern, objtype):
        if isinstance(self, objtype) and pattern == self.name:
            return [self]
        else:
            return []


class AbstractType(JuliaModelNode):
    __fields__ = ("name", "templateparameters", "parenttype", "docstring")

    def match(self, pattern, objtype):
        if isinstance(self, objtype) and pattern == self.name:
            return [self]
        else:
            return []


class Function(JuliaModelNode):
    __fields__ = ("name", "modulename", "templateparameters", "signature", "docstring")

    def match(self, pattern, objtype):
        namepattern, *signaturepattern = pattern.split("(")
        if isinstance(self, objtype) and pattern == self.name:
            return [self]
        else:
            return []


class Field(JuliaModel):
    __fields__ = ("name", "fieldtype", "value")


class Signature(JuliaModel):
    __fields__ = ("positionalarguments", "optionalarguments", "keywordarguments", "varargsname", "kwvarargsname")


class Argument(JuliaModel):
    __fields__ = ("name", "argumenttype", "value")
