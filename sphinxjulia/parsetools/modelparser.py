import os
import subprocess
import model

scriptdir = "scripts"
scripts = {
    "file": "sourcefile2pythonmodel.jl",
    "abstracttype": "parse_abstracttype.jl",
    "compositetype": "parse_compositetype.jl",
    "module": "parse_module.jl",
    "function": "parse_function.jl"
}

eval_environment = {x: getattr(model, x) for x in dir(model) if not x.startswith("_")}

class JuliaParser:
    cached_files = {}

    def parsefile(self, sourcepath):
        if not os.path.exists(sourcepath):
            raise ValueError("Can't find file: " + sourcepath)
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
    return scope, text


def parse_argumentstring(text):
    d = {}
    if "=" in text:
        text, value = text.split("=", 1)
        d["value"] = value.strip()
    if "::" in text:
        text, argtype = text.split("::", 1)
        d["argumenttype"] = argtype.strip()
    return model.Argument(name=text.strip(), **d)


def parse_signaturestring(text):
    d = {
        "positionalarguments": [],
        "keywordarguments": [],
    }
    argumenttype = "positionalarguments"
    arguments = d[argumenttype]
    i_start = 0
    i = 0
    while i < len(text):
        x = text[i]
        if x in brackets:
            i_closing = find_closing_bracket(text, i, x)
            assert i_closing != -1
            i = i_closing
        elif x == ";":
            argumenttype = "keywordarguments"
        elif x == "," or i+1 == len(text):
            if x == ",":
                argstring = text[i_start:i].strip()
            else:
                argstring = text[i_start:i+1].strip()
            if argstring.endswith("..."):
                arg = parse_argumentstring(argstring[:-3])
                if argumenttype == "positionalarguments":
                    d["vararg"] = arg
                else:
                    d["kwvararg"] = arg
            else:
                d[argumenttype].append(parse_argumentstring(argstring))
            i_start = i+1
        i += 1
    return model.Signature(**d)


def parse_functionstring(text):
    d = {}
    i_sig0 = text.find("(")
    i_sig1 = text.rfind(")")
    assert i_sig0 != -1 and i_sig1 != -1 and i_sig0 < i_sig1
    i_templ0 = text.find("{")
    i_templ1 = text.find("}", i_templ0)
    if i_templ0 != -1 and i_templ0 < i_sig0:
        assert i_templ1 < i_sig0
        name = text[:i_templ0].strip()
        templateparameters = text[i_templ0+1:i_templ1].split(",")
        d["templateparameters"] = [t.strip() for t in templateparameters]
    else:
        d["templateparameters"] = []
        name = text[:i_sig0].strip()
    if "." in name:
        modulename, name = name.rsplit(".", 1)
        d["modulename"] = modulename.strip()
    d["name"] = name.strip()
    d["signature"] = parse_signaturestring(text[i_sig0+1:i_sig1])
    return d


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