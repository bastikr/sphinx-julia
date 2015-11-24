import re
import sphinx
import docutils


def matchingbracket(buf, i0):
    N = len(buf)
    count = 1
    for i in range(i0+1, N):
        if buf[i] == '(':
            count += 1
        elif buf[i] == ')':
            count -= 1
        if count == 0:
            return i
    return None


def getfunction(sourcepath, functionname):
    f = open(sourcepath)
    buf = f.read()
    f.close()

    functionregex = "function {}".format(functionname) + "[\{\[]"
    r = re.search(functionregex, buf)
    if r is None:
        raise ValueError()
    i0 = r.start()

    # Extract docstring
    if buf[i0-4:i0] == '"""\n':
        i1 = buf.rindex('"""', 0, i0-4)
        docstring = buf[i1+4:i0-5]

    # Extract function definition
    i1 = matchingbracket(buf, buf.index("(", i0))
    functionstring = buf[i0:i1+1]
    return docstring, functionstring


class Function(docutils.nodes.General, docutils.nodes.Element):
    pass


class FunctionDirective(docutils.parsers.rst.Directive):
    has_content = True
    required_arguments = 2

    def run(self):
        sourcename = self.arguments[0]
        functionname = self.arguments[1]
        docstring, functionstring = getfunction(sourcename, functionname)
        formatstring = ".. code-block:: julia\n\n    "
        data = formatstring + functionstring + "\n\n" + docstring
        content = docutils.statemachine.ViewList(data.splitlines(), sourcename)
        node = docutils.nodes.paragraph()
        self.state.nested_parse(content, 0, node)
        return [node]


def visit_function_node(self, node):
    pass


def depart_function_node(self, node):
    pass


def setup(app):
    app.add_config_value('autodocjulia_basedir', '..', 'html')

    app.add_node(Function,
                 html=(visit_function_node, depart_function_node),
                 latex=(visit_function_node, depart_function_node),
                 text=(visit_function_node, depart_function_node))

    app.add_directive('juliafunction', FunctionDirective)
    # app.connect('doctree-resolved', process_todo_nodes)
    # app.connect('env-purge-doc', purge_todos)

    return {'version': '0.1'}