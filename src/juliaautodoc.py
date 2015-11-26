import os
import docutils
import juliadomain
import sphinx.ext.napoleon


class FunctionDirective(docutils.parsers.rst.Directive):
    has_content = False
    required_arguments = 2

    def __init__(self, name, arguments, options, content, lineno,
                content_offset, block_text, state, state_machine):
        docutils.parsers.rst.Directive.__init__(
                self, name, arguments, options, content, lineno,
                content_offset, block_text, state, state_machine)
        self._directive = juliadomain.JuliaFunction(
                "function", ["<auto>"], {}, docutils.statemachine.ViewList(),
                lineno, content_offset, block_text, state, state_machine)

    def run(self):
        env = self.state.document.settings.env
        sourcedir = env.app.config.juliaautodoc_basedir
        sourcename = self.arguments[0]
        sourcepath = os.path.join(sourcedir, sourcename)
        functionname = self.arguments[1]
        function = env.juliaparser.function_from_file(sourcepath, functionname)
        docstringlines = function["docstring"].split("\n")
        env.app.emit('autodoc-process-docstring',
                                  "function", function["name"], None,
                                  {}, docstringlines)
        function["docstring"] = "\n".join(docstringlines)
        self._directive.function = function
        return self._directive.run()


# Ugly hack to use :kwparam: in napoleon docstring parsing.
def _parse_keyword_arguments_section(self, section):
    fields = self._consume_fields()
    if self._config.napoleon_use_param:
        lines = []
        for _name, _type, _desc in fields:
            field = ':kwparam %s: ' % _name
            lines.extend(self._format_block(field, _desc))
            if _type:
                lines.append(':kwtype %s: %s' % (_name, _type))
        return lines + ['']
    else:
        return self._format_fields('Keyword Parameters', fields)

sphinx.ext.napoleon.docstring.GoogleDocstring._parse_keyword_arguments_section = _parse_keyword_arguments_section


def setup(app):
    app.add_config_value('juliaautodoc_basedir', '..', 'html')
    app.add_directive('jl:autofunction', FunctionDirective)
    app.add_event('autodoc-process-docstring')
    app.add_event('autodoc-skip-member')
    return {'version': '0.1'}
