from docutils.parsers.rst import Directive

import model


class AutoDirective(Directive):
    has_content = False
    required_arguments = 2
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        self.env = self.state.document.settings.env
        sourcepath = self.arguments[0]
        module = self.env.juliaparser.parsefile(sourcepath)
        objects = module.match(self.arguments[1], self.modelclass)
        nodes = []
        for obj in objects:
            nodes.extend(obj.create_nodes(self))
        return nodes

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


class AutoFileDirective(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        self.env = self.state.document.settings.env
        sourcepath = self.arguments[0]
        module = self.env.juliaparser.parsefile(sourcepath)
        return module.create_nodes(self)


class AutoModuleDirective(AutoDirective):
    modelclass = model.Module

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


class AutoFunctionDirective(AutoDirective):
    modelclass = model.Function


class AutoCompositeType(AutoDirective):
    modelclass = model.CompositeType


class AutoAbstractType(AutoDirective):
    modelclass = model.AbstractType


def setup(app):
    # app.add_config_value('juliaautodoc_basedir', '..', 'html')
    app.add_directive('jl:autofile', AutoFileDirective)
    app.add_directive('jl:automodule', AutoModuleDirective)
    app.add_directive('jl:autofunction', AutoFunctionDirective)
    app.add_directive('jl:autotype', AutoCompositeType)
    app.add_directive('jl:autoabstract', AutoAbstractType)
    app.add_event('autodoc-process-docstring')
    app.add_event('autodoc-skip-member')
