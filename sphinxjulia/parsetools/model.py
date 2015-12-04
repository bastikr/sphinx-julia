from docutils import nodes
from docutils.statemachine import ViewList

import hashlib
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

    def setid(self, directive):
        scope = directive.env.ref_context['jl:scope']
        if scope:
            self["ids"] = [".".join(scope) + "." + self.name]
        else:
            self["ids"] = [self.name]

    def register(self, env):
        d = env.domaindata['jl'][self.typeidentifier]
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

    def create_nodes(self, directive):
        self.setid(directive)
        self.register(directive.env)
        self.append(self.parsedocstring(directive))
        return [self]

    def parsedocstring(self, directive):
        docstringlines = self.docstring.split("\n")
        directive.env.app.emit('autodoc-process-docstring',
                               'class', self["ids"][0], self, {}, docstringlines)
        content = ViewList(docstringlines)
        docstringnode = nodes.paragraph()
        directive.state.nested_parse(content, directive.content_offset,
                                     docstringnode)
        return docstringnode


class Module(JuliaModelNode):
    typeidentifier = "module"
    __fields__ = ("name", "body", "docstring")

    def create_nodes(self, directive):
        # Unnamed module (parsed file without toplevel module)
        if self.name == "":
            self["ids"] = [""]
            self.append(self.parsedocstring(directive))
            for n in self.body:
                self.extend(n.create_nodes(directive))
            return self.children
        # Normal module
        self.setid(directive)
        self.register(directive.env)
        scope = directive.env.ref_context['jl:scope']
        scope.append(self.name)
        self.append(self.parsedocstring(directive))
        for n in self.body:
            self.extend(n.create_nodes(directive))
        scope.pop()
        return [self]

    def match(self, pattern, objtype):
        l = []
        if isinstance(self, objtype) and pattern == self.name:
            l.append(self)
        for obj in self.body:
                l.extend(obj.match(pattern, objtype))
        return l


class CompositeType(JuliaModelNode):
    typeidentifier = "type"
    __fields__ = ("name", "templateparameters", "parenttype", "fields", "constructors", "docstring")

    def match(self, pattern, objtype):
        if isinstance(self, objtype) and pattern == self.name:
            return [self]
        else:
            return []


class AbstractType(JuliaModelNode):
    typeidentifier = "abstract"
    __fields__ = ("name", "templateparameters", "parenttype", "docstring")

    def match(self, pattern, objtype):
        if isinstance(self, objtype) and pattern == self.name:
            return [self]
        else:
            return []


class Function(JuliaModelNode):
    typeidentifier = "function"
    __fields__ = ("name", "modulename", "templateparameters", "signature", "docstring")
    hashfunc = hashlib.md5()

    def setid(self, directive):
        scope = directive.env.ref_context['jl:scope']
        x = bytes(str(self.templateparameters) + str(self.signature), "UTF-16")
        self.hashfunc.update(x)
        name = self.name + "-" + self.hashfunc.hexdigest()
        if scope:
            self["ids"] = [".".join(scope) + "." + name]
        else:
            self["ids"] = [name]

    def register(self, env):
        pass
        #env.domaindata['jl'][type(self)][self.name] = (env.docname, self)

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
