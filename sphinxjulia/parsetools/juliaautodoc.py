from docutils.parsers.rst import Directive
# import sphinx.ext.napoleon
import model


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


class AutoFunctionDirective(Directive):
    has_content = False
    required_arguments = 2
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        self.env = self.state.document.settings.env
        sourcepath = self.arguments[0]
        module = self.env.juliaparser.parsefile(sourcepath)
        functions = module.match_content(model.Function, self.arguments[1])
        nodes = []
        for function in functions:
            nodes.extend(function.create_nodes(self))
        return nodes


class AutoCompositeType(Directive):
    has_content = False
    required_arguments = 2
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        self.env = self.state.document.settings.env
        sourcepath = self.arguments[0]
        m = self.env.juliaparser.parsefile(sourcepath)
        types = m.match_content(model.CompositeType, self.arguments[1])
        nodes = []
        for t in types:
            nodes.extend(t.create_nodes(self))
        return nodes


class AutoAbstractType(Directive):
    has_content = False
    required_arguments = 2
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        self.env = self.state.document.settings.env
        sourcepath = self.arguments[0]
        module = self.env.juliaparser.parsefile(sourcepath)
        types = module.match_content(model.AbstractType, self.arguments[1])
        nodes = []
        for t in types:
            nodes.extend(t.create_nodes(self))
        return nodes


# Ugly hack to use :kwparam: in napoleon docstring parsing.
# def _parse_keyword_arguments_section(self, section):
#     fields = self._consume_fields()
#     if self._config.napoleon_use_param:
#         lines = []
#         for _name, _type, _desc in fields:
#             field = ':kwparam %s: ' % _name
#             lines.extend(self._format_block(field, _desc))
#             if _type:
#                 lines.append(':kwtype %s: %s' % (_name, _type))
#         return lines + ['']
#     else:
#         return self._format_fields('Keyword Parameters', fields)

# sphinx.ext.napoleon.docstring.GoogleDocstring._parse_keyword_arguments_section = _parse_keyword_arguments_section


def setup(app):
    # app.add_config_value('juliaautodoc_basedir', '..', 'html')
    app.add_directive('jl:autofile', AutoFileDirective)
    app.add_directive('jl:autofunction', AutoFunctionDirective)
    app.add_directive('jl:autotype', AutoCompositeType)
    app.add_directive('jl:autoabstract', AutoAbstractType)
    app.add_event('autodoc-process-docstring')
    app.add_event('autodoc-skip-member')
    return {'version': '0.1'}
