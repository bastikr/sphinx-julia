import re
import os
import tempfile
import subprocess
import sphinx
import docutils
import juliadomain


def matchingbracket(buf, i0):
    N = len(buf)
    count = 1
    for i in range(i0+1, N):
        if buf[i] == '(':
            count += 1
        elif buf[i] == ')':
            count -= 1
        if count == 0:
            return i
    return None


def getfunction(sourcepath, functionname):
    f = tempfile.NamedTemporaryFile(mode='r', delete=True)
    directory = os.path.dirname(os.path.realpath(__file__))
    scriptpath = os.path.join(directory, "parsefile.jl")
    subprocess.call(["julia", scriptpath, sourcepath, f.name])
    buf = f.read()
    f.close()
    d = eval(buf)
    for func in d:
        if func["name"] == functionname:
            return func
    raise ValueError()
    # functionregex = "function {}".format(functionname) + "[\{\(]"
    # r = re.search(functionregex, buf)
    # if r is None:
    #     raise ValueError()
    # i0 = r.start()

    # # Extract docstring
    # if buf[i0-4:i0] == '"""\n':
    #     i1 = buf.rindex('"""', 0, i0-4)
    #     docstring = buf[i1+4:i0-5]

    # # Extract function definition
    # i1 = matchingbracket(buf, buf.index("(", i0))
    # functionstring = buf[i0:i1+1]
    # return docstring, functionstring


# class Function(docutils.nodes.General, docutils.nodes.Element):
#     pass

def parse_argument(arg):
    d = {}
    x = arg.split("::")
    if len(x) == 2:
        d["name"] = x[0].strip()
        x = x[1].split("=")
        d["type"] = x[0].strip()
        if len(x) == 2:
            d["default"] = x[1].strip()
    else:
        x = arg.split("=")
        d["name"] = x[0].strip()
        if len(x) == 2:
            d["default"] = x[1].strip()
    return d


def parse_argumentlist(funcarguments):
    x = funcarguments.split(";")
    args = [parse_argument(arg) for arg in x[0].split(",") if arg.strip()]
    if len(x) == 1:
        kwargs = []
    elif len(x) == 2:
        kwargs = [parse_argument(arg) for arg in x[1].split(",") if arg.strip()]
    else:
        raise ValueError()
    return args, kwargs

signature_regex = re.compile(
    r'''^ (?P<qualifiers>[\w.]*\.)?
          (?P<name>\w+)  \s*
          (?: \{(?P<templateparameters>.*)\})?
          (?: \((?P<arguments>.*)\)
          )? $
          ''', re.VERBOSE)


def parse_function(funcstring):
    m = signature_regex.match(funcstring)
    if m is None:
        raise ValueError
    d = m.groupdict()
    # qualifiers = d.get("qualifiers", "")
    # name = d["name"]
    # templateparameters = d.get("templateparameters", "")
    argumentlist = d.pop("arguments", "")
    args, kwargs = parse_argumentlist(argumentlist)
    d["args"] = args
    d["kwargs"] = kwargs
    return d


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

    def run(self):
        sourcename = self.arguments[0]
        functionname = self.arguments[1]
        funcdict = getfunction(sourcename, functionname)
        self.domain, self.objtype = 'jl', 'Function'

        node = sphinx.addnodes.desc()
        node.document = self.state.document
        node['domain'] = self.domain
        # 'desctype' is a backwards compatible attribute
        node['objtype'] = node['desctype'] = self.objtype
        node['noindex'] = noindex = ('noindex' in self.options)
        fullname = funcdict["name"]
        if funcdict["templateparameters"]:
            fullname += "{" + ",".join(funcdict["templateparameters"]) + "}"

        signaturenode = sphinx.addnodes.desc_signature("test", "")
        node += signaturenode
        contentnode = sphinx.addnodes.desc_content()
        node += contentnode

        # d = docutils.nodes.paragraph(funcdict["docstring"], funcdict["docstring"])
        d = docutils.statemachine.ViewList(funcdict["docstring"].split("\n"))
        self.state.nested_parse(d, self.content_offset, contentnode)
        # raise(Exception(d))
        signaturenode += sphinx.addnodes.desc_name(fullname, fullname)
        paramlist = sphinx.addnodes.desc_parameterlist()
        signaturenode += paramlist
        for arg in funcdict["arguments"]:
            x = arg["name"]
            paramlist += sphinx.addnodes.desc_parameter(x, x)
        for arg in funcdict["kwarguments"]:
            x = arg["name"]
            paramlist += juliadomain.desc_keyparameter(x, x)

        return [node]
        raise(Exception(funcdict))
        # docstring, funcstring = getfunction(sourcename, functionname)

        # Parse function
        funcstring = funcstring.replace("function ", "").strip()
        funcstring = re.sub("\n *", " ", funcstring)
        funcdict = parse_function(funcstring)


        # Parse docstring
        header, arguments = parse_docstring(docstring)
        header = "    " + header.replace("\n", "    \n")

        # Render functionsignature
        funcsig = ""
        if "modifiers" in funcdict:
            funcsig += funcdict["modifiers"] + "."
        funcsig += funcdict["name"]
        if funcdict.get("templateparameters", None) is not None:
            funcsig += "{{{}}}".format(funcdict["templateparameters"])
        funcsig += "("
        funcsig += ",".join([arg["name"] for arg in funcdict["args"]])
        if funcdict["kwargs"]:
            funcsig += ";"
            funcsig += ",".join([arg["name"] for arg in funcdict["kwargs"]])
        funcsig += ")"

        func = ".. jl:function:: " + funcsig

        params = []
        for name, desc in arguments.get("Arguments", []):
            argtype = ""
            for arg in funcdict["args"]:
                if arg["name"] == name:
                    argtype = arg.get("type", "")
                    break
            params.append("    :param {} {}: {}".format(argtype, name, desc))

        kwparams = []
        for name, desc in arguments.get("Optional Arguments", []):
            argtype = ""
            for arg in funcdict["kwargs"]:
                if arg["name"] == name:
                    argtype = arg.get("type", "")
                    break
            kwparams.append("    :param {} {}: {}".format(argtype, name, desc))
        data = "\n\n".join([func, header, "\n".join(params+kwparams)])
        content = docutils.statemachine.ViewList(data.splitlines(), sourcename)
        node = docutils.nodes.paragraph()
        self.state.nested_parse(content, 0, node)
        return [node]


def visit_function_node(self, node):
    pass


def depart_function_node(self, node):
    pass


def setup(app):
    app.add_config_value('juliaautodoc_basedir', '..', 'html')

    app.add_directive('jl:autofunction', FunctionDirective)
    # app.connect('doctree-resolved', process_todo_nodes)
    # app.connect('env-purge-doc', purge_todos)

    return {'version': '0.1'}