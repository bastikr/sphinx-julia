

def format_signature(signature):
    arguments = signature.positionalarguments + signature.optionalarguments
    first = True
    l = []
    for arg in arguments:
        if not first:
            l.append(", ")
        else:
            first = False
        l.append(format_argument(arg))
    if signature.keywordarguments:
        l.append(";")
    first = True
    for arg in signature.keywordarguments:
        if not first:
            l.append(", ")
        else:
            first = False
        l.append(format_argument(arg))
    return "".join(l)


def format_argument(argument):
    return "<em>" + argument.name + "</em>"


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


def visit_compositetype(translator, node):
    tpars = format_templateparameters(node.templateparameters)
    partype = format_parenttype(node.parenttype)
    visit_generic(translator, node, "type", node.name + tpars + partype)


def visit_abstracttype(translator, node):
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
    I(node.name + tpars)
    I('</code>')
    I('<span class="sig-paren">(</span>')
    I(signature)
    I('<span class="sig-paren">)</span>')
    translator.add_permalink_ref(node, "Permalink to this function")
    I("</dt><dd>")

TranslatorFunctions = {
    "Module": (visit_module, depart_generic),
    "AbstractType": (visit_abstracttype, depart_generic),
    "CompositeType": (visit_compositetype, depart_generic),
    "Function":  (visit_function, depart_generic)
}
