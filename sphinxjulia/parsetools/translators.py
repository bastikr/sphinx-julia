import model

nodes = ["Module", "CompositeType", "AbstractType", "Function"]

templates = {
    "AbstractType": [
        '''
        <dl class="class">
          <dt>
            <em class="property">abstract </em>
            <code class="descname">{name}{tpars}{parent}</code>
          </dt>
          <dd>
        ''',
        '''
          </dd>
        </dl>
        '''],
    "CompositeType": [
        '''
        <dl class="class">
          <dt>
            <em class="property">type </em>
            <code class="descname">{name}{tpars}{parent}</code>
          </dt>
          <dd>
        ''',
        '''
          </dd>
        </dl>
        '''],
    "Function": [
        '''
        <dl class="function">
          <dt>
            <em class="property">function </em>
            <code class="descname">{name}{tpars}</code>
            <span class="sig-paren">(</span>
                {signature}
            <span class="sig-paren">)</span>
          </dt>
          <dd>
        ''',
        '''
          </dd>
        </dl>
        '''],
    "Module": [
        '''
        <dl class="module">
          <dt>
            <em class="property">module </em>
            <code class="descname">{name}</code>
          </dt>
          <dd class="body">
        ''',
        '''
          </dd>
        </dl>
        ''']
}


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
        t = templates["Module"][0]
        x = t.format(name=node.name)
        self.body.append(x)

    def depart_Module(self, node):
        self.body.append(templates["Module"][1])

    def visit_CompositeType(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        t = templates["CompositeType"][0]
        x = t.format(name=node.name, tpars=tpars, parent=node.parenttype)
        self.body.append(x)

    def depart_CompositeType(self, node):
        self.body.append(templates["CompositeType"][1])

    def visit_AbstractType(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        t = templates["AbstractType"][0]
        x = t.format(name=node.name, tpars=tpars, parent=node.parenttype)
        self.body.append(x)

    def depart_AbstractType(self, node):
        self.body.append(templates["AbstractType"][1])

    def visit_Function(self, node):
        if node.templateparameters:
            tpars = "{%s}" % ",".join(node.templateparameters)
        else:
            tpars = ""
        signature = handle_signature(node.signature)
        t = templates["Function"][0]
        x = t.format(name=node.name, tpars=tpars, signature=signature)
        self.body.append(x)

    def depart_Function(self, node):
        self.body.append(templates["Function"][1])
