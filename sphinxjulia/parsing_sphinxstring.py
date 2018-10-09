"""
Convert a string written for Sphinx to its corresponding JuliaModel.
"""

from . import model

from sphinx.util import logging
logger = logging.getLogger(__name__)


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
            _appendargument(d, text[i_start:i].strip(), argtype)
            argtype = "keywordarguments"
            i_start = i+1
        elif x == ",":
            _appendargument(d, text[i_start:i].strip(), argtype)
            i_start = i+1
        i += 1
    if text[-1] != ";":
        _appendargument(d, text[i_start:].strip(), argtype)
    return model.Signature(**d)


def parse_functionstring(text):
    d = {}

    i_parentheses_open = text.find("(")
    if i_parentheses_open == -1:
        qualifiedname = text.strip()
    else:
        qualifiedname = text[:i_parentheses_open]

    if "." in qualifiedname:
        modulename, name = qualifiedname.rsplit(".", 1)
        d["modulename"] = modulename.strip()
    else:
        name = qualifiedname
    d["name"] = name.strip()

    if i_parentheses_open == -1:
        return model.Function(**d)

    i_parentheses_close = find_closing_bracket(text, i_parentheses_open, "(")
    if i_parentheses_close == -1:
        logger.error("Failed parsing function string (Unbalanced parentheses):\n" + text)
        raise ValueError("Failed parsing function string (Unbalanced parentheses)")

    d["signature"] = parse_signaturestring(text[i_parentheses_open+1:i_parentheses_close])

    text = text[i_parentheses_close:]
    i_where = text.find(" where ")
    if i_where != -1:
        i_brace_open = text.find("{", i_where)
        if i_brace_open == -1:
            logger.error("Failed parsing function string (Missing { after where clause):\n" + text)
            raise ValueError("Failed parsing function string (Missing { after where clause)")
        i_brace_close = find_closing_bracket(text, i_brace_open, "{")
        if i_brace_close == -1:
            logger.error("Failed parsing function string (Missing } after where clause):\n" + text)
            raise ValueError("Failed parsing function string (Missing } after where clause)")
        templateparameters = text[i_brace_open+1:i_brace_close].split(",")
        d["templateparameters"] = [t.strip() for t in templateparameters]
        text = text[:i_where]

    if text.startswith("::"):
        d["returntype"] = text[2:].strip()

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
