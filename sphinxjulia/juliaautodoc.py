import os

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList
from sphinx.util.docfields import Field, GroupedField, TypedField
from sphinx.util.docfields import DocFieldTransformer
from sphinx.locale import l_

from . import model, modelparser, query


class AutoDirective(Directive):
    has_content = False
    required_arguments = 2
    optional_arguments = 0
    final_argument_whitespace = False

    doc_field_types = []

    def run(self):
        if ':' in self.name:
            self.domain, self.objtype = self.name.split(':', 1)
        else:
            self.domain, self.objtype = '', self.name
        self.objtype = self.objtype[len("auto"):]
        self.env = self.state.document.settings.env
        sourcedir = self.env.app.config.juliaautodoc_basedir
        self.sourcepath = os.path.join(sourcedir, self.arguments[0])
        self.matches = []

        # Load all julia objects from file
        modulenode = self.env.juliaparser.parsefile(self.sourcepath)
        # Store nodes matching the search pattern in self.matches
        self.filter(modulenode)
        if len(self.matches) == 0:
            args = self.arguments
            raise ValueError('No matches for directive "{}" in '
                             ' file "{}" with arguments {}'.format(
                                    self.objtype, args[0], str(args[1:])))

        scope = self.env.ref_context.get('jl:scope', [])
        for node in self.matches:
            # Set ids and register nodes in global index
            query.walk_tree(node, self.register, scope)
            # Add docstrings
            query.walk_tree(node, self.docstring, scope)
        return self.matches

    def filter(self, modulenode):
        self.pattern = modelparser.parse(self.objtype, self.arguments[1])
        query.walk_tree(modulenode, self.match, scope=[])

    def match(self, node, scope):
        if query.match(self.pattern, node):
            self.matches.append(node)

    def register(self, node, scope):
        if isinstance(node, model.JuliaModelNode):
            objtype = type(node).__name__.lower()
            node["ids"] = [node.uid(scope)]
            dictionary = self.env.domaindata['jl'][objtype]
            node["ids"] = [node.uid(scope)]
            node.register(self.env.docname, scope, dictionary)

    def docstring(self, node, scope):
        docstringlines = node.docstring.split("\n")
        self.env.app.emit('autodoc-process-docstring',
                          'class', node["ids"][0], node, {}, docstringlines)
        content = ViewList(docstringlines)
        docstringnode = nodes.paragraph()
        self.state.nested_parse(content, self.content_offset,
                                docstringnode)
        DocFieldTransformer(self).transform_all(docstringnode)
        node.insert(0, docstringnode)


class AutoFileDirective(AutoDirective):
    required_arguments = 1

    def filter(self, modulenode):
        # Take all elements of file
        self.matches.extend(modulenode.children)


class AutoModuleDirective(AutoDirective):
    pass


class AutoFunctionDirective(AutoDirective):
    final_argument_whitespace = True

    doc_field_types = [
        TypedField('parameter', label=l_('Parameters'),
                   names=('param', 'parameter', 'arg', 'argument'),
                   typerolename='obj', typenames=('paramtype', 'type'),
                   can_collapse=True),
        TypedField('kwparam', label=l_('Keyword Parameters'),
                   names=('kwparam', 'kwparameter', 'kwarg', 'kwargument'),
                   typerolename='obj', typenames=('kwparamtype', 'kwtype'),
                   can_collapse=True),
        GroupedField('exceptions', label=l_('Exceptions'), rolename='exc',
                     names=('raises', 'raise', 'exception', 'except'),
                     can_collapse=True),
        Field('returnvalue', label=l_('Returns'), has_arg=False,
              names=('returns', 'return')),
        Field('returntype', label=l_('Return type'), has_arg=False,
              names=('rtype',), bodyrolename='obj'),
    ]


class AutoType(AutoDirective):
    pass


class AutoAbstract(AutoDirective):
    pass


def setup(app):
    # Config values
    app.add_config_value('juliaautodoc_basedir', '..', 'html')

    # Directives
    app.add_directive('jl:autofile', AutoFileDirective)
    app.add_directive('jl:automodule', AutoModuleDirective)
    app.add_directive('jl:autofunction', AutoFunctionDirective)
    app.add_directive('jl:autotype', AutoType)
    app.add_directive('jl:autoabstract', AutoAbstract)

    # Events
    app.add_event('autodoc-process-docstring')
    app.add_event('autodoc-skip-member')
