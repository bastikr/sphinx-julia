import re
import sphinx
import docutils
import juliadomain





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
        sourcename = self.arguments[0]
        functionname = self.arguments[1]
        function = env.juliaparser.function_from_file(sourcename, functionname)
        docstringlines = function["docstring"].split("\n")
        env.app.emit('autodoc-process-docstring',
                                  "function", function["name"], None,
                                  {}, docstringlines)
        function["docstring"] = "\n".join(docstringlines)
        self._directive.function = function
        return self._directive.run()


def setup(app):
    app.add_config_value('juliaautodoc_basedir', '..', 'html')
    app.add_directive('jl:autofunction', FunctionDirective)
    app.add_event('autodoc-process-docstring')
    app.add_event('autodoc-skip-member')
    return {'version': '0.1'}
