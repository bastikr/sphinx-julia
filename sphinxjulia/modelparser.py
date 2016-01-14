import os
import subprocess
from . import model

scriptdir = "parsetools/scripts"
scripts = {
    "file": "sourcefile2pythonmodel.jl",
}

eval_environment = {x: getattr(model, x) for x in dir(model) if not x.startswith("_")}


class JuliaParser:
    cached_files = {}

    def parsefile(self, sourcepath):
        sourcepath = os.path.realpath(sourcepath)
        if not os.path.exists(sourcepath):
            raise ValueError("Can't find file: " + sourcepath)
        if sourcepath in self.cached_files:
            return self.cached_files[sourcepath]
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, scriptdir, scripts["file"])
        p = subprocess.Popen(["julia", scriptpath, sourcepath],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
        (buf, err) = p.communicate()
        if err:
            raise Exception(err)
        model = eval(buf, eval_environment)
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
            raise Exception(err)
        model = eval(buf, eval_environment)
        return model


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
            assert i_closing != -1
            i = i_closing
        elif x == ";":
            argtype = "keywordarguments"
        elif x == ",":
            _appendargument(d, text[i_start:i].strip(), argtype)
            i_start = i+1
        i += 1
    if text[-1] != ";":
        _appendargument(d, text[i_start:].strip(), argtype)
    return model.Signature(**d)


def parse_functionstring(text):
    d = {}
    i_sig0 = text.find("(")
    i_sig1 = text.rfind(")")
    if i_sig0 == -1:
        d["name"] = text
        return model.Function(**d)
    assert i_sig0 < i_sig1
    i_templ0 = text.find("{")
    i_templ1 = text.find("}", i_templ0)
    if i_templ0 != -1 and i_templ0 < i_sig0:
        assert i_templ1 < i_sig0
        name = text[:i_templ0].strip()
        templateparameters = text[i_templ0+1:i_templ1].split(",")
        d["templateparameters"] = [t.strip() for t in templateparameters]
    else:
        name = text[:i_sig0].strip()
    if "." in name:
        modulename, name = name.rsplit(".", 1)
        d["modulename"] = modulename.strip()
    d["name"] = name.strip()
    d["signature"] = parse_signaturestring(text[i_sig0+1:i_sig1])
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
