

def format_signature(translator, signature):
    arguments = signature.positionalarguments + signature.optionalarguments
    args = [format_argument(translator, arg) for arg in arguments]
    if signature.varargs is not None:
        args.append(format_argument(translator, signature.varargs) + r"\ldots")
    if not (signature.keywordarguments or signature.kwvarargs):
        return ", ".join(args)
    kwargs = [format_argument(translator, arg) for arg in signature.keywordarguments]
    if signature.kwvarargs is not None:
        kwargs.append(format_argument(translator, signature.kwvarargs) + r"\ldots")
    return ", ".join(args) + "; " + ", ".join(kwargs)


def format_argument(translator, argument):
    out = r"\emph{%s}" % translator.encode(argument.name)
    if argument.macrocall:
        out = r"{\scriptsize %s} " % translator.encode(argument.macrocall) + out
    if argument.argumenttype:
        out += "::" + translator.encode(argument.argumenttype)
    if argument.value:
        out += r" = \texttt{%s}" % translator.encode(argument.value)
    return out


def format_templateparameters(translator, args):
    if args:
        return "{%s}" % ",".join([arg for arg in args])
    else:
        return ""


def format_parenttype(translator, arg):
    if arg:
        return " <: " + arg
    else:
        return ""


def visit_generic(translator, node, descriptor, name):
    I = translator.body.append
    I('\n\\begin{fulllineitems}\n')
    I(r'\phantomsection')
    I('\\pysigline{\\textbf{%s} %s}\\ \n' % (
        translator.encode(descriptor),
        translator.encode(name),))


def depart_generic(translator, node):
    translator.body.append("\\end{fulllineitems}\n")


def visit_module(translator, node):
    visit_generic(translator, node, "module", node.name)


def visit_type(translator, node):
    tpars = format_templateparameters(translator, node.templateparameters)
    partype = format_parenttype(translator, node.parenttype)
    visit_generic(translator, node, "type", node.name + tpars + partype)


def visit_abstract(translator, node):
    tpars = format_templateparameters(translator, node.templateparameters)
    partype = format_parenttype(translator, node.parenttype)
    visit_generic(translator, node, "abstract", node.name + tpars + partype)


def visit_function(translator, node):
    name = (r'\textbf{\texttt{%s}}' % translator.encode(node.name))
    signature = format_signature(translator, node.signature)
    tpars = format_templateparameters(translator, node.templateparameters)
    if tpars:
        tpars = translator.encode(" where " + tpars)
    I = translator.body.append
    I('\n\\begin{fulllineitems}\n')
    I(r'\phantomsection')
    I(r'\label{index:%s}' % node["ids"][0])
    I('\\pysiglinewithargsret{\\textbf{function} %s}{%s}{%s}\n' % (name, signature, tpars))

    # I('<dl class="function">')
    # I('<dt id="%s">' % node["ids"][0])
    # I('<em class="property">function </em>')
    # I('<code class="descname">')
    # I(node.name + tpars)
    # I('</code>')
    # I('<span class="sig-paren">(</span>')
    # I(signature)
    # I('<span class="sig-paren">)</span>')
    # translator.add_permalink_ref(node, "Permalink to this function")
    # I("</dt><dd>")

TranslatorFunctions = {
    "Module": (visit_module, depart_generic),
    "Abstract": (visit_abstract, depart_generic),
    "Type": (visit_type, depart_generic),
    "Function":  (visit_function, depart_generic)
}
