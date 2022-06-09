

def format_signature(signature):
    arguments = signature.positionalarguments + signature.optionalarguments
    args = [format_argument(arg) for arg in arguments]
    if signature.varargs is not None:
        args.append(format_argument(signature.varargs) + "...")
    if not (signature.keywordarguments or signature.kwvarargs):
        return ", ".join(args)
    kwargs = [format_argument(arg) for arg in signature.keywordarguments]
    if signature.kwvarargs is not None:
        kwargs.append(format_argument(signature.kwvarargs) + "...")
    return ", ".join(args) + "; " + ", ".join(kwargs)


def format_argument(argument):
    out = "<em>" + argument.name + "</em>"
    if argument.macrocall:
        out = "<small>" + argument.macrocall + "</small> " + out
    if argument.argumenttype:
        out += "::" + argument.argumenttype
    if argument.value:
        out += " = <tt>" + argument.value + "</tt>"
    return out


def format_templateparameters(args):
    if args:
        return "{%s}" % ",".join(args)
    else:
        return ""


def format_parenttype(args):
    if args:
        return "<: " + args
    else:
        return ""


def visit_generic(translator, node, descriptor, signature):
    I = translator.body.append
    I('<dl class="class">')
    I('<dt id=%s>' % node["ids"][0])
    I('<em class="property">%s </em>' % descriptor)
    I('<code class="descname">')
    I(signature)
    I('</code>')
    translator.add_permalink_ref(node, "Permalink to this" + descriptor)
    I('</dt><dd class="body">')


def depart_generic(translator, node):
    translator.body.append("</dd></dl>")


def visit_module(translator, node):
    visit_generic(translator, node, "module", node.name)


def visit_type(translator, node):
    tpars = format_templateparameters(node.templateparameters)
    partype = format_parenttype(node.parenttype)
    visit_generic(translator, node, "type", node.name + tpars + partype)


def visit_abstract(translator, node):
    tpars = format_templateparameters(node.templateparameters)
    partype = format_parenttype(node.parenttype)
    visit_generic(translator, node, "abstract", node.name + tpars + partype)


def visit_function(translator, node):
    tpars = format_templateparameters(node.templateparameters)
    signature = format_signature(node.signature)
    I = translator.body.append
    I('<dl class="function">')
    I('<dt id="%s">' % node["ids"][0])
    I('<em class="property">function </em>')
    I('<code class="descname">')
    I(node.name)
    I('</code>')
    I('<span class="sig-paren">(</span>')
    I(signature)
    I('<span class="sig-paren">)</span>')
    if tpars:
        I(" where " + tpars)
    translator.add_permalink_ref(node, "Permalink to this function")
    I("</dt><dd>")

TranslatorFunctions = {
    "Module": (visit_module, depart_generic),
    "Abstract": (visit_abstract, depart_generic),
    "Type": (visit_type, depart_generic),
    "Function":  (visit_function, depart_generic)
}
