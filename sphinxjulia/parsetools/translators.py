import model

nodes = ["Module", "CompositeType", "AbstractType", "Function"]

abstracttype_template = '''
<dl class="class">
  <dt>
    <em class="property">abstract </em>
    <code class="descname">{name}{tpars}{parent}</code>
  </dt>
  <dd>
    {docstring}
  </dd>
</dl>
'''

compositetype_template = '''
<dl class="class">
  <dt>
    <em class="property">type </em>
    <code class="descname">{name}{tpars}{parent}</code>
  </dt>
  <dd>
    {docstring}
  </dd>
</dl>
'''

function_template = '''
<dl class="function">
  <dt>
    <em class="property">function </em>
    <code class="descname">{name}{tpars}</code>
    <span class="sig-paren">(</span>
        {signature}
    <span class="sig-paren">)</span>
  </dt>
  <dd>
    {docstring}
  </dd>
</dl>
'''

module_template = '''
<dl class="module">
  <dt>
    <em class="property">module </em>
    <code class="descname">{name}</code>
  </dt>
  <dd>
    {docstring}
    ||subnodes||
  </dd>
</dl>
'''


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
    if signature.optionalarguments:
        l.append(";")
    for arg in signature.optionalarguments:
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
        x = module_template.format(name=node.name, docstring=node.docstring)
        x1, x2 = x.split("||subnodes||")
        self.body.append(x1)

        if node.orderedobjects:
            subnodes = node.orderedobjects
        else:
            subnodes = node.abstracttypes + node.compositetypes + node.functions
        for x in subnodes:
            if isinstance(x, model.AbstractType):
                self.visit_AbstractType(x)
                self.depart_AbstractType(x)
            elif isinstance(x, model.CompositeType):
                self.visit_CompositeType(x)
                self.depart_CompositeType(x)
            elif isinstance(x, model.Function):
                self.visit_Function(x)
                self.depart_Function(x)
            else:
                self.body.append("<p>%s</p>" % str(x))
        self.body.append(x2)

    def depart_Module(self, node):
        pass

    def visit_CompositeType(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        if node.docstring:
            docs = "<p>%s</p>" % node.docstring
        else:
            docs = ""
        x = compositetype_template.format(name=node.name, tpars=tpars,
                                          parent=node.parenttype,
                                          docstring=docs)
        self.body.append(x)

    def depart_CompositeType(self, node):
        pass

    def visit_AbstractType(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        if node.docstring:
            docs = "<p>%s</p>" % node.docstring
        else:
            docs = ""
        x = abstracttype_template.format(name=node.name, tpars=tpars,
                                         parent=node.parenttype,
                                         docstring=docs)
        self.body.append(x)

    def depart_AbstractType(self, node):
        pass

    def visit_Function(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        if node.docstring:
            docs = "<p>%s</p>" % node.docstring
        else:
            docs = ""
        signature = handle_signature(node.signature)
        x = function_template.format(name=node.name, tpars=tpars,
                                     signature=signature,
                                     docstring=docs)
        self.body.append(x)

    def depart_Function(self, node):
        pass
