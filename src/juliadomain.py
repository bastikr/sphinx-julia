# -*- coding: utf-8 -*-
"""
sphinx.domains.julia
~~~~~~~~~~~~~~~~~~~~

The Julia domain.

:copyright: Copyright 2015 by Sebastian Krämer
:license: BSD, see LICENSE for details.
"""

import docutils
from docutils import nodes

import sphinx
from sphinx.locale import l_
from sphinx.util.docfields import Field, GroupedField, TypedField

import juliaparser


class desc_keyparameter(nodes.Part, nodes.Inline, nodes.TextElement):
    """
    Node for a keyword parameter.
    """


class JuliaFunction(sphinx.directives.ObjectDescription):
    """
    Julia function directive.
    """

    option_spec = {
        # 'noindex': directives.flag,
        # 'module': directives.unchanged,
    }

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

    def needs_arglist(self):
        return True

    def handle_signature(self, sig, signode):
        """
        Transform a Julia function signature into RST nodes.
        """
        env = self.state.document.settings.env

        # Directive was invoked from autodoc
        if sig == "<auto>":
            function = self.function
            content = docutils.statemachine.ViewList(function["docstring"].split("\n"))
            self.content = content
        # Directive was invoked normally
        else:
            functionstring = "function " + sig + "end"
            function = env.juliaparser.parsefunction(functionstring)

        # Full function name: name{T}
        # modules are not handled at the moment
        fullname = function["name"]
        if function["templateparameters"]:
            fullname += "{" + ",".join(function["templateparameters"]) + "}"

        # Create RST noded
        signode['fullname'] = fullname
        signode += sphinx.addnodes.desc_name(fullname, fullname)
        paramlist = sphinx.addnodes.desc_parameterlist()
        signode += paramlist
        for arg in function["arguments"]:
            x = arg["name"]
            paramlist += sphinx.addnodes.desc_parameter(x, x)
        for arg in function["kwarguments"]:
            x = arg["name"]
            paramlist += desc_keyparameter(x, x)
        return fullname


class JuliaDomain(sphinx.domains.Domain):
    """
    Julia language domain.
    """
    name = 'jl'
    label = 'Julia'
    object_types = {
        'function': sphinx.domains.ObjType(l_('function'), 'func', 'obj'),
        # 'global':          ObjType(l_('global variable'),  'global', 'obj'),
        # 'class':            ObjType(l_('class'),            'class', 'obj'),
        # 'exception':       ObjType(l_('exception'),        'exc', 'obj'),
        # 'attribute':       ObjType(l_('attribute'),        'attr', 'obj'),
        # 'const':           ObjType(l_('const'),            'const', 'obj'),
        # 'module':          ObjType(l_('module'),           'mod', 'obj'),
    }

    directives = {
        'function':        JuliaFunction,
        # 'global':          JuliaGloballevel,
        # 'const':           JuliaEverywhere,
        # 'class':            JuliaClasslike,
        # 'exception':       JuliaClasslike,
        # 'attribute':     JuliaAttribute,
        # 'module':          JuliaModule,
    }

    roles = {
        # 'func':   JuliaXRefRole(fix_parens=False),
        # 'global': JuliaXRefRole(),
        # 'class':  JuliaXRefRole(),
        # 'exc':    JuliaXRefRole(),
        # 'attr':   JuliaXRefRole(),
        # 'const':  JuliaXRefRole(),
        # 'mod':    JuliaXRefRole(),
        # 'obj':    JuliaXRefRole(),
    }

    initial_data = {
        'objects': {},  # fullname -> docname, objtype
        'modules': {},  # modname -> docname, synopsis, platform, deprecated
    }
    indices = [
        # JuliaModuleIndex,
    ]

def visit_desc_keyparameter(self, node):
    if self.first_kwordparam:
        self.first_kwordparam = False
        self.body.append('; ')
    else:
        self.body.append(', ')
    if not node.hasattr('noemph'):
        self.body.append('<em>')


def depart_desc_keyparameter(self, node):
    if not node.hasattr('noemph'):
        self.body.append('</em>')


def update_builder(app):
    app.env.juliaparser = juliaparser.JuliaParser()
    translator = app.builder.translator_class
    # raise Exception(translator)
    translator.first_kwordparam = True
    _visit_desc_parameterlist = translator.visit_desc_parameterlist
    def visit_desc_parameterlist(self, node):
        self.first_kwordparam = True
        _visit_desc_parameterlist(self, node)
    #f = types.MethodType(visit_desc_parameterlist, translator)
    translator.visit_desc_parameterlist = visit_desc_parameterlist


def setup(app):
    app.add_node(desc_keyparameter,
                html=(visit_desc_keyparameter, depart_desc_keyparameter)
                )
    app.connect('builder-inited', update_builder)
    app.add_domain(JuliaDomain)
