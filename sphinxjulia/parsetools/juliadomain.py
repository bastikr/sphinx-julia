# xrefs
# directives
import model
import modelparser

from docutils.parsers.rst import Directive, directives
import sphinx
import sphinx.domains
from sphinx import addnodes


class JuliaDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'noindex': directives.flag,
    }

    def parse(self):
        return []

    def run(self):
        if ':' in self.name:
            self.domain, self.objtype = self.name.split(':', 1)
        else:
            self.domain, self.objtype = '', self.name
        self.env = self.state.document.settings.env
        self.indexnode = addnodes.index(entries=[])
        return self.parse()


class ModuleDirective(JuliaDirective):
    def parse(self):
        text = "module " + self.arguments[0] + "\nend"
        m = self.env.juliaparser.parsestring("module", text)
        contentnode = addnodes.desc_content()
        self.state.nested_parse(self.content, self.content_offset, contentnode)
        m.orderedobjects = []
        for node in contentnode:
            m.orderedobjects.append(node)
            if isinstance(node, model.AbstractType):
                m.abstracttypes.append(node)
            elif isinstance(node, model.CompositeType):
                m.compositetypes.append(node)
            elif isinstance(node, model.Function):
                m.functions.append(node)
        # self.env.app.warn(contentnode)
        return [m]


class FunctionDirective(JuliaDirective):
    def parse(self):
        text = "function " + self.arguments[0] + "\nend"
        m = self.env.juliaparser.parsestring("function", text)
        m.docstring = "".join(self.content).strip()
        return [m]


class AbstractTypeDirective(JuliaDirective):
    def parse(self):
        text = "abstract " + self.arguments[0]
        m = self.env.juliaparser.parsestring("abstracttype", text)
        m.docstring = "".join(self.content).strip()
        return [m]


class CompositeTypeDirective(JuliaDirective):
    def parse(self):
        text = "type " + self.arguments[0] + "\nend"
        m = self.env.juliaparser.parsestring("compositetype", text)
        m.docstring = "".join(self.content).strip()
        return [m]


class JuliaDomain(sphinx.domains.Domain):
    """
    Julia language domain.
    """
    name = 'jl'
    label = 'Julia'
    object_types = {
        # 'function': sphinx.domains.ObjType(l_('function'), 'func', 'obj'),
        # 'global':          ObjType(l_('global variable'),  'global', 'obj'),
        # 'class':            ObjType(l_('class'),            'class', 'obj'),
        # 'exception':       ObjType(l_('exception'),        'exc', 'obj'),
        # 'attribute':       ObjType(l_('attribute'),        'attr', 'obj'),
        # 'const':           ObjType(l_('const'),            'const', 'obj'),
        # 'module':          ObjType(l_('module'),           'mod', 'obj'),
    }

    directives = {
        'function':         FunctionDirective,
        'abstracttype':     AbstractTypeDirective,
        'type':             CompositeTypeDirective,
        'module':           ModuleDirective,
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


def update_builder(app):
    #app.warn(str(parser))
    app.env.juliaparser = modelparser.JuliaParser()
    # translator = app.builder.translator_class
    # translator.first_kwordparam = True
    # _visit_desc_parameterlist = translator.visit_desc_parameterlist
    # def visit_desc_parameterlist(self, node):
    #     self.first_kwordparam = True
    #     _visit_desc_parameterlist(self, node)
    # translator.visit_desc_parameterlist = visit_desc_parameterlist

import translators

def setup(app):
    # app.add_config_value('julia_signature_show_qualifier', True, 'html')
    # app.add_config_value('julia_signature_show_type', True, 'html')
    # app.add_config_value('julia_signature_show_default', True, 'html')
    # app.add_config_value('julia_docstring_show_type', True, 'html')

    for nodename in translators.nodes:
        visit = getattr(translators.HTML, "visit_" + nodename)
        depart = getattr(translators.HTML, "depart_" + nodename)
        app.add_node(getattr(model, nodename),
                html=(visit, depart)
                )
    # app.add_node(model.Module,
    #             #html=(visit_desc_keyparameter, depart_desc_keyparameter)
    #             )
    # app.add_node(model.Function,
    #             #html=(visit_desc_keyparameter, depart_desc_keyparameter)
    #             )
    # app.add_node(model.AbstractType,
    #             # html=(visit_desc_keyparameter, depart_desc_keyparameter)
    #             )
    # app.add_node(model.CompositeType,
    #             # html=(visit_desc_keyparameter, depart_desc_keyparameter)
    #             )
    app.connect('builder-inited', update_builder)
    app.add_domain(JuliaDomain)