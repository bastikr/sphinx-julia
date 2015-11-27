# -*- coding: utf-8 -*-
"""
sphinx.domains.julia
~~~~~~~~~~~~~~~~~~~~

The Julia domain.

:copyright: Copyright 2015 by Sebastian Krämer
:license: BSD, see LICENSE for details.
"""

from six import iteritems

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList

import sphinx
from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import make_refnode
from sphinx.util.compat import Directive
from sphinx.util.docfields import Field, GroupedField, TypedField

from . import parser


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
            content = ViewList(function["docstring"].split("\n"))
            self.content = content
        # Directive was invoked normally
        else:
            functionstring = "function " + sig + "end"
            function = env.juliaparser.parsefunction(functionstring)
            self.function = function

        # Full function name: name{T}
        # modules are not handled at the moment
        fullname = ""
        if env.config.julia_signature_show_qualifier and function["qualifier"]:
            fullname += function["qualifier"] + "."
        fullname +=  function["name"]
        if function["templateparameters"]:
            fullname += "{" + ",".join(function["templateparameters"]) + "}"

        # Create RST noded
        signode['fullname'] = fullname
        signode += sphinx.addnodes.desc_name(fullname, fullname)
        paramlist = sphinx.addnodes.desc_parameterlist()
        signode += paramlist
        for arg in function["arguments"]:
            x = arg["name"]
            if env.config.julia_signature_show_type and arg["type"]:
                x += "::" + arg["type"]
            if env.config.julia_signature_show_default and arg["value"]:
                x += "=" + arg["value"]
            paramlist += sphinx.addnodes.desc_parameter(x, x)
        for arg in function["kwarguments"]:
            x = arg["name"]
            if env.config.julia_signature_show_type and arg["type"]:
                x += "::" + arg["type"]
            if env.config.julia_signature_show_default and arg["value"]:
                x += "=" + arg["value"]
            paramlist += desc_keyparameter(x, x)
        return fullname

    def before_content(self):
        env = self.state.document.settings.env
        if env.config.julia_docstring_show_type:
            l = []
            for arg in self.function["arguments"]:
                if arg["type"]:
                    l.append(":type {name}: :class:`{type}`\n".format(**arg))
            for arg in self.function["kwarguments"]:
                if arg["type"]:
                    l.append(":kwtype {name}: :class:`{type}`\n".format(**arg))
            self.content.append(ViewList(l))


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
    app.env.juliaparser = parser.JuliaParser()
    translator = app.builder.translator_class
    translator.first_kwordparam = True
    _visit_desc_parameterlist = translator.visit_desc_parameterlist
    def visit_desc_parameterlist(self, node):
        self.first_kwordparam = True
        _visit_desc_parameterlist(self, node)
    translator.visit_desc_parameterlist = visit_desc_parameterlist


def setup(app):
    app.add_config_value('julia_signature_show_qualifier', True, 'html')
    app.add_config_value('julia_signature_show_type', True, 'html')
    app.add_config_value('julia_signature_show_default', True, 'html')
    app.add_config_value('julia_docstring_show_type', True, 'html')

    app.add_node(desc_keyparameter,
                html=(visit_desc_keyparameter, depart_desc_keyparameter)
                )
    app.connect('builder-inited', update_builder)
    app.add_domain(JuliaDomain)
