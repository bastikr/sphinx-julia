import model

nodes = ["Module", "CompositeType", "AbstractType", "Field", "Function", "Signature", "Argument"]

abstracttype_template = '''
<dl class="class">
  <dt>
    <em class="property">abstract </em>
    <code class="descname">{name}{tpars}{parent}</code>
  </dt>
</dl>
'''

compositetype_template = '''
<dl class="class">
  <dt>
    <em class="property">type </em>
    <code class="descname">{name}{tpars}{parent}</code>
  </dt>
</dl>
'''

function_template = '''
<dl class="function">
  <dt>
    <em class="property">function </em>
    <code class="descname">{name}{tpars}</code>
    <span class="sig-paren">(</span>
        ||signature||
    <span class="sig-paren">)</span>
  </dt>
</dl>
'''

module_template = '''
<dl class="module">
  <dt>
    <em class="property">module </em>
    <code class="descname">{name}</code>
        ||subnodes||
  </dt>
</dl>
'''

class HTML:

    def visit_Module(self, node):
        x = module_template.format(name=node.name)
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
        self.body.append(x2)

    def depart_Module(self, node):
        pass

    def visit_CompositeType(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        x = compositetype_template.format(name=node.name, tpars=tpars,
                                          parent=node.parenttype)
        self.body.append(x)

    def depart_CompositeType(self, node):
        pass

    def visit_AbstractType(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        x = abstracttype_template.format(name=node.name, tpars=tpars,
                                          parent=node.parenttype)
        self.body.append(x)

    def depart_AbstractType(self, node):
        pass

    def visit_Field(self, node):
        self.body.append("Field")

    def depart_Field(self, node):
        pass

    def visit_Function(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        x = function_template.format(name=node.name, tpars=tpars)
        x1, x2 = x.split("||signature||")
        self.body.append(x1)
        self.visit_Signature(node.signature)
        self.depart_Signature(node.signature)
        self.body.append(x2)

    def depart_Function(self, node):
        pass

    def visit_Signature(self, node):
        arguments = node.positionalarguments + node.optionalarguments
        first = True
        for arg in arguments:
            if not first:
                self.body.append(", ")
            else:
                first = False
            self.visit_Argument(arg)
            self.depart_Argument(arg)
        if node.optionalarguments:
            self.body.append(";")
        for arg in node.optionalarguments:
            self.visit_Argument(arg)
            self.depart_Argument(arg)

    def depart_Signature(self, node):
        pass

    def visit_Argument(self, node):
        name = "<em>" + node.name + "</em>"
        self.body.append(node.name)

    def depart_Argument(self, node):
        pass
