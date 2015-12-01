import model

nodes = ["Module", "CompositeType", "AbstractType", "Function"]


def handle_signature(signature):
    arguments = signature.positionalarguments + signature.optionalarguments
    first = True
    l = []
    for arg in arguments:
        if not first:
            l.append(", ")
        else:
            first = False
        l.append(handle_argument(arg))
    if signature.keywordarguments:
        l.append(";")
    first = True
    for arg in signature.keywordarguments:
        if not first:
            l.append(", ")
        else:
            first = False
        l.append(handle_argument(arg))
    return "".join(l)


def handle_argument(argument):
    return "<em>" + argument.name + "</em>"


class HTML:

    def visit_Module(self, node):
        I = self.body.append
        I('<dl class="module">')
        I('<dt id={}>'.format(node["ids"][0]))
        I('<em class="property">module </em>')
        I('<code class="descname">')
        I(node.name)
        I('</code>')
        self.add_permalink_ref(node, "Permalink to this module")
        I('</dt><dd class="body">')

    def depart_Module(self, node):
        self.body.append("</dd></dl>")

    def visit_CompositeType(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        if node.parenttype:
            parent = "<: " + node.parenttype
        else:
            parent = ""
        I = self.body.append
        I('<dl class="class">')
        I('<dt id={}>'.format(node["ids"][0]))
        I('<em class="property">type </em>')
        I('<code class="descname">')
        I(node.name + tpars + parent)
        I('</code>')
        self.add_permalink_ref(node, "Permalink to this composite type")
        I('</dt><dd>')

    def depart_CompositeType(self, node):
        self.body.append("</dd></dl>")

    def visit_AbstractType(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        if node.parenttype:
            parent = "<: " + node.parenttype
        else:
            parent = ""
        I = self.body.append
        I('<dl class="class">')
        I('<dt id={}>'.format(node["ids"][0]))
        I('<em class="property">abstract </em>')
        I('<code class="descname">')
        I(node.name + tpars + parent)
        I('</code>')
        self.add_permalink_ref(node, "Permalink to this abstract type")
        I('</dt><dd>')

    def depart_AbstractType(self, node):
        self.body.append("</dd></dl>")

    def visit_Function(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        signature = handle_signature(node.signature)
        I = self.body.append
        I('<dl class="function">')
        I('<dt id="{}">'.format(node["ids"][0]))
        I('<em class="property">function </em>')
        I('<code class="descname">{}{}</code>'.format(node.name, tpars))
        I('<span class="sig-paren">(</span>')
        I(signature)
        I('<span class="sig-paren">)</span>')
        self.add_permalink_ref(node, "Permalink to this function")
        I("</dt><dd>")

    def depart_Function(self, node):
        self.body.append('</dd></dl>')
