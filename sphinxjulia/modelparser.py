from __future__ import unicode_literals

import os
import subprocess
from . import model

try:
    import julia
except ImportError:
    print("PyJulia not found - using slower alternative.")
    julia = None

scriptdir = "parsetools/scripts"
scripts = {
    "file": "sourcefile2pythonmodel.jl",
}
eval_environment = {x: getattr(model, x) for x in dir(model) if not x.startswith("_")}

class ParseError(Exception):
    def __init__(self, source, errormessage):
        self.source = source
        self.errormessage = errormessage


class JuliaParser:
    cached_files = {}
    _julia = None

    @property
    def julia(self):
        if isinstance(self._julia, Exception):
            return None
        elif self._julia is None:
            try:
                self._julia = julia.Julia()
            except Exception as e:
                print("Creating julia.Julia raised an error - falling back to slower alternative.")
                self._julia = e
                return None
        return self._julia

    def parsefile(self, sourcepath):
        sourcepath = os.path.realpath(sourcepath)
        if not os.path.exists(sourcepath):
            raise ValueError("Can't find file: " + sourcepath)
        if sourcepath in self.cached_files:
            return self.cached_files[sourcepath]
        if self.julia:
            return self.parsefile_pyjulia(sourcepath)
        else:
            return self.parsefile_script(sourcepath)

    def parsefile_pyjulia(self, sourcepath):
        j = self.julia
        current_dir= os.path.dirname(os.path.realpath(__file__))
        parsetools_dir = os.path.join(current_dir, "parsetools/src/")

        j.eval('push!(LOAD_PATH, "{}")'.format(parsetools_dir))
        j.eval('using parsetools')
        j.eval('model = parsetools.reader.read_file("{}")'.format(sourcepath))
        text = j.eval('string(model)')
        model = eval(text, eval_environment)
        self.cached_files[sourcepath] = model
        return model

    def parsefile_script(self, sourcepath):
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, scriptdir, scripts["file"])
        p = subprocess.Popen(["julia", scriptpath, sourcepath],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (buf, err) = p.communicate()
        if p.returncode != 0:
            print("Parsing file {} failed with error message:".format(sourcepath))
            print("-"*80)
            print(err.decode("utf-8"))
            print("-"*80)
            raise ParseError(sourcepath, err)
        # buf is a bytestring in utf-8 encoding.
        text = buf.decode("utf-8")
        model = eval(text, eval_environment)
        self.cached_files[sourcepath] = model
        return model

    def parsestring(self, objtype, text):
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, scriptdir, scripts[objtype])
        p = subprocess.Popen(["julia", scriptpath, text],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
        (buf, err) = p.communicate()
        if err:
            print("Parsing {} from string:".format(objtype))
            print("-"*80)
            print(text)
            print("-"*80)
            print("failed with error message:")
            print("-"*80)
            print(err.decode("utf-8"))
            print("-"*80)
            raise ParseError(text, err)
        model = eval(buf, eval_environment)
        return model

    def __getstate__(self):
        return {"cached_files": self.cached_files}


def splitscope(text):
    if "." in text:
        scope, name = text.rsplit(".", 1)
        scope = scope.split(".")
    else:
        scope, name = [], text
    return scope, name


def parse_modulestring(text):
    return model.Module(name=text)


def typestring2dict(text):
    d = {}
    if "<:" in text:
        text, parenttype = text.split("<:", 1)
        d["parenttype"] = parenttype.strip()
    if "{" in text:
        text, templ = text.split("{", 1)
        templ = templ.strip()
        assert templ[-1] == "}"
        templateparameters = templ[:-1].split(",")
        d["templateparameters"] = [t.strip() for t in templateparameters]
    d["name"] = text.strip()
    return d


def parse_abstractstring(text):
    return model.Abstract(**typestring2dict(text))


def parse_typestring(text):
    return model.Type(**typestring2dict(text))


def parse_argumentstring(text):
    d = {}
    if "=" in text:
        text, value = text.split("=", 1)
        d["value"] = value.strip()
    if "::" in text:
        text, argtype = text.split("::", 1)
        d["argumenttype"] = argtype.strip()
    return model.Argument(name=text.strip(), **d)


def _appendargument(d, argstring, argtype):
    if argstring.endswith("..."):
        arg = parse_argumentstring(argstring[:-3])
        if argtype == "positionalarguments":
            d["varargs"] = arg
        else:
            d["kwvarargs"] = arg
    else:
        d[argtype].append(parse_argumentstring(argstring))


def parse_signaturestring(text):
    text = text.strip()
    if len(text) == 0:
        return model.Signature()
    d = {
        "positionalarguments": [],
        "keywordarguments": [],
    }
    argtype = "positionalarguments"
    i_start = 0
    i = 0
    while i < len(text):
        x = text[i]
        if x in brackets:
            i_closing = find_closing_bracket(text, i, x)
            if i_closing == -1:
                raise ValueError("Bracket '{}' opens at index {}."
                                 "Couldn't find the closing bracket:\n{}"
                                 "".format(x, i, repr(text)))
            i = i_closing
        elif x == ";":
            argtype = "keywordarguments"
            _appendargument(d, text[i_start:i].strip(), argtype)
            i_start = i+1
        elif x == ",":
            _appendargument(d, text[i_start:i].strip(), argtype)
            i_start = i+1
        i += 1
    if text[-1] != ";":
        _appendargument(d, text[i_start:].strip(), argtype)
    return model.Signature(**d)


def parse_functionstring(text):
    def f(s, sub):
        i = s.find(sub)
        if i==-1:
            i = len(s)
        return i

    d = {}

    i_braces = f(text, "{")
    i_parentheses = f(text, "(")
    i_returntype = f(text, "->")

    # Test for template parameters
    if i_braces < i_parentheses and i_braces < i_returntype:
        i_close = find_closing_bracket(text, i_braces, "{")
        assert i_close != -1
        templateparameters = text[i_braces+1:i_close].split(",")
        d["templateparameters"] = [t.strip() for t in templateparameters]
        text = text[:i_braces] + text[i_close+1:]
        i_parentheses = f(text, "(")
        i_returntype = f(text, "->")

    # Test for calling signature
    if i_parentheses < i_returntype:
        i_close = find_closing_bracket(text, i_parentheses, "(")
        assert i_close != -1
        d["signature"] = parse_signaturestring(text[i_parentheses+1:i_close])
        text = text[:i_parentheses] + text[i_close+1:]
        i_returntype = f(text, "->")

    # Test for return type annotation
    if i_returntype < len(text):
        d["returntype"] = text[i_returntype + 2:]
        text = text[:i_returntype]

    # Text only contains the function name at this point
    if "." in text:
        modulename, name = text.rsplit(".", 1)
        d["modulename"] = modulename.strip()
    else:
        name = text
    d["name"] = name.strip()

    return model.Function(**d)


brackets = {
    "(": ")",
    "[": "]",
    "{": "}"
}


def find_closing_bracket(text, start, openbracket):
    closebracket = brackets[openbracket]
    counter = 0
    for i in range(start, len(text)):
        if text[i] == openbracket:
            counter += 1
        elif text[i] == closebracket:
            counter -= 1
        if counter == 0:
            return i
    return -1


def parse(objtype, text):
    f = eval("parse_%sstring" % objtype)
    return f(text)
