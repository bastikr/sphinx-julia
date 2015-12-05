from docutils import nodes
import docutils.utils
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList

import model
import query


class AutoDirective(Directive):
    has_content = False
    required_arguments = 2
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        if ':' in self.name:
            self.domain, self.objtype = self.name.split(':', 1)
        else:
            self.domain, self.objtype = '', self.name
        self.objtype = self.objtype[len("auto"):]
        self.env = self.state.document.settings.env
        sourcepath = self.arguments[0]
        targetstring = self.arguments[1]
        modulenode = self.env.juliaparser.parsefile(sourcepath)
        catalog = query.catalog_tree(modulenode, scope=[])
        matches = query.find_object_by_string(self.objtype, [],
                                              targetstring, catalog)
        scope = self.env.ref_context['jl:scope']
        docname = self.env.docname
        dictionaries = self.env.domaindata['jl']
        self.document = docutils.utils.new_document("")
        for node in matches:
            # Add nodes to index and set their ids
            query.catalog_tree(node, scope, docname, dictionaries)
            # Add docstrings
            node.walk(self)
        return matches

    def dispatch_visit(self, node):
        if isinstance(node, model.JuliaModelNode):
            self.add_docstring(node)

    def add_docstring(self, node):
        docstringlines = node.docstring.split("\n")
        self.env.app.emit('autodoc-process-docstring',
                          'class', node["ids"][0], node, {}, docstringlines)
        content = ViewList(docstringlines)
        docstringnode = nodes.paragraph()
        self.state.nested_parse(content, self.content_offset,
                                docstringnode)
        node.insert(0, docstringnode)


class AutoFileDirective(AutoDirective):
    required_arguments = 1

    def run(self):
        if ':' in self.name:
            self.domain, self.objtype = self.name.split(':', 1)
        else:
            self.domain, self.objtype = '', self.name
        self.objtype = self.objtype[len("auto"):]
        self.env = self.state.document.settings.env
        sourcepath = self.arguments[0]
        modulenode = self.env.juliaparser.parsefile(sourcepath)
        scope = self.env.ref_context['jl:scope']
        docname = self.env.docname
        dictionaries = self.env.domaindata['jl']
        self.document = docutils.utils.new_document("")
        for node in modulenode.body:
            # Add nodes to index and set their ids
            query.catalog_tree(node, scope, docname, dictionaries)
            # Add docstrings
            node.walk(self)
        return modulenode.body


class AutoModuleDirective(AutoDirective):
    pass


class AutoFunctionDirective(AutoDirective):
    final_argument_whitespace = True


class AutoType(AutoDirective):
    pass


class AutoAbstract(AutoDirective):
    pass


def setup(app):
    # app.add_config_value('juliaautodoc_basedir', '..', 'html')
    app.add_directive('jl:autofile', AutoFileDirective)
    app.add_directive('jl:automodule', AutoModuleDirective)
    app.add_directive('jl:autofunction', AutoFunctionDirective)
    app.add_directive('jl:autotype', AutoType)
    app.add_directive('jl:autoabstract', AutoAbstract)
    app.add_event('autodoc-process-docstring')
    app.add_event('autodoc-skip-member')
