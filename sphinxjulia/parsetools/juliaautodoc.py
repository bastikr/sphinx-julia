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
            nodes.append(obj.create_node(self))
        return nodes


class AutoFileDirective(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        self.env = self.state.document.settings.env
        sourcepath = self.arguments[0]
        module = self.env.juliaparser.parsefile(sourcepath)
        m = module.create_node(self)
        if module.name == "": # No top-level module in the file
            return m.children
        else:
            return [m]


class AutoModuleDirective(AutoDirective):
    modelclass = model.Module


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
