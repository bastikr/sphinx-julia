import re
import os
import tempfile
import subprocess
import sphinx
import docutils
import juliadomain


def getfunction(sourcepath, functionname):
    directory = os.path.dirname(os.path.realpath(__file__))
    scriptpath = os.path.join(directory, "parsefile.jl")
    p = subprocess.Popen(["julia", scriptpath, sourcepath],
            stdout=subprocess.PIPE, universal_newlines=True)
    (buf, err) = p.communicate()
    d = eval(buf)
    for func in d:
        if func["name"] == functionname:
            return func
    raise ValueError()


def parse_docstringarguments(argumentsection):
    terms = re.split("\n\s{4}(?=\w)", argumentsection)
    arguments = []
    for term in terms:
        if not term.strip():
            continue
        name, description = term.split("\n", 1)
        name = name.strip()
        description = description.strip().replace("\n" + " "*8, " ")
        arguments.append([name, description])
    return arguments


def parse_docstring(docstring):
    arguments = {}
    s = docstring.split("\n**Arguments**\n")
    header = s[0].strip("\n ")
    if len(s) != 2:
        return header, arguments
    s = s[1].split("\n**Optional Arguments**\n")
    arguments["Arguments"] = parse_docstringarguments(s[0])
    if len(s) != 2:
        return header, arguments
    arguments["Optional Arguments"] = parse_docstringarguments(s[1])
    return header, arguments


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
        sourcename = self.arguments[0]
        functionname = self.arguments[1]
        funcdict = getfunction(sourcename, functionname)
        self._directive.funcdict = funcdict
        return self._directive.run()


def setup(app):
    app.add_config_value('juliaautodoc_basedir', '..', 'html')
    app.add_directive('jl:autofunction', FunctionDirective)


    return {'version': '0.1'}