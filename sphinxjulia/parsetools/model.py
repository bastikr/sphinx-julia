from docutils import nodes
from docutils.statemachine import ViewList

import sphinx


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

    def subnodes(self, directive):
        return []

    def create_nodes(self, directive):
        self.children = sphinx.addnodes.desc_content()
        docstringnode = self.parsedocstring(directive)
        self.children += docstringnode
        subnodes = self.subnodes(directive)
        for node in subnodes:
            self.children += node
        return [self]

    def parsedocstring(self, directive):
        classname = self.__class__.__name__
        docstringlines = self.docstring.split("\n")
        directive.env.app.emit('autodoc-process-docstring',
                               classname, self.name, None, {}, docstringlines)
        content = ViewList(docstringlines)
        docstringnode = sphinx.addnodes.desc_content()
        directive.state.nested_parse(content, directive.content_offset,
                                     docstringnode)
        return docstringnode


class Module(JuliaModelNode):
    orderedobjects = None
    __fields__ = ("name", "modules", "abstracttypes", "compositetypes", "functions", "docstring")

    def subnodes(self, directive):
        l = []
        for n in self.modules + self.abstracttypes + self.compositetypes + self.functions:
            l.extend(n.create_nodes(directive))
        return l

    def match_functions(self, pattern):
        *modulepattern, funcpattern = pattern.split(".")
        l = []
        for module in self.modules:
            l.extend(module.match_functions(pattern))
        for function in self.functions:
            if function.match(funcpattern):
                l.append(function)
        return l

    def match_abstracttypes(self, pattern):
        *modulepattern, typepattern = pattern.split(".")
        l = []
        for module in self.modules:
            l.extend(module.match_abstracttypes(pattern))
        for t in self.abstracttypes:
            if t.match(typepattern):
                l.append(t)
        return l

    def match_compositetypes(self, pattern):
        *modulepattern, typepattern = pattern.split(".")
        l = []
        for module in self.modules:
            l.extend(module.match_compositetypes(pattern))
        for t in self.compositetypes:
            if t.match(typepattern):
                l.append(t)
        return l


class CompositeType(JuliaModelNode):
    __fields__ = ("name", "templateparameters", "parenttype", "fields", "constructors", "docstring")

    def match(self, pattern):
        if pattern == self.name:
            return True
        else:
            return False


class AbstractType(JuliaModelNode):
    __fields__ = ("name", "templateparameters", "parenttype", "docstring")

    def match(self, pattern):
        if pattern == self.name:
            return True
        else:
            return False


class Function(JuliaModelNode):
    __fields__ = ("name", "modulename", "templateparameters", "signature", "docstring")

    def match(self, pattern):
        namepattern, *signaturepattern = pattern.split("(")
        if namepattern == self.name:
            return True
        else:
            return False

class Field(JuliaModel):
    __fields__ = ("name", "fieldtype", "value")


class Signature(JuliaModel):
    __fields__ = ("positionalarguments", "optionalarguments", "keywordarguments", "varargsname", "kwvarargsname")


class Argument(JuliaModel):
    __fields__ = ("name", "argumenttype", "value")
