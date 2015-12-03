from docutils import nodes
from docutils.parsers.rst import Directive

from sphinx import addnodes
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode

import model
import modelparser
import translators


class JuliaDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def parse(self):
        return []

    def run(self):
        if ':' in self.name:
            self.domain, self.objtype = self.name.split(':', 1)
        else:
            self.domain, self.objtype = '', self.name
        self.env = self.state.document.settings.env
        modelnode = self.parse()
        self.env.domaindata['jl'][type(modelnode)].append(modelnode)
        self.env.ref_context['jl:scope'].append(modelnode.name)
        self.state.nested_parse(self.content, self.content_offset, modelnode)
        self.env.ref_context['jl:scope'].pop()
        return [modelnode]


class ModuleDirective(JuliaDirective):

    def parse(self):
        text = "module " + self.arguments[0] + "\nend"
        m = self.env.juliaparser.parsestring("module", text)
        return m


class FunctionDirective(JuliaDirective):

    def parse(self):
        text = "function " + self.arguments[0] + "\nend"
        m = self.env.juliaparser.parsestring("function", text)
        return m


class AbstractTypeDirective(JuliaDirective):

    def parse(self):
        text = "abstract " + self.arguments[0]
        m = self.env.juliaparser.parsestring("abstracttype", text)
        return m


class CompositeTypeDirective(JuliaDirective):

    def parse(self):
        text = "type " + self.arguments[0] + "\nend"
        m = self.env.juliaparser.parsestring("compositetype", text)
        return m


class JuliaXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        refnode['jl:scope'] = env.ref_context['jl:scope'].copy()
        if not has_explicit_title:
            title = title.lstrip('.')    # only has a meaning for the target
            target = target.lstrip('~')  # only has a meaning for the title
            # if the first character is a tilde, don't display the module/class
            # parts of the contents
            if title[0:1] == '~':
                title = title[1:]
                dot = title.rfind('.')
                if dot != -1:
                    title = title[dot+1:]
        # if the first character is a dot, search more specific namespaces first
        # else search builtins first
        if target[0:1] == '.':
            target = target[1:]
            refnode['refspecific'] = True
        return title, target


class JuliaDomain(Domain):
    """
    Julia language domain.
    """
    name = 'jl'
    label = 'Julia'
    object_types = {
        'function': ObjType(l_('function'), 'func'),
        'type': ObjType(l_('type'), 'type'),
        'abstract': ObjType(l_('abstract'), 'abstract'),
        'module': ObjType(l_('module'), 'mod'),
    }

    directives = {
        'function': FunctionDirective,
        'abstract': AbstractTypeDirective,
        'type': CompositeTypeDirective,
        'module': ModuleDirective,
    }

    roles = {
        'func': JuliaXRefRole(fix_parens=False),
        'type':  JuliaXRefRole(),
        'abstract': JuliaXRefRole(),
        'mod':    JuliaXRefRole(),
    }

    initial_data = {
        model.Module: {},
        model.Function: {},
        model.AbstractType: {},
        model.CompositeType: {}
        # 'objects': {},  # fullname -> docname, objtype
        # 'modules': {},  # modname -> docname, synopsis, platform, deprecated
    }
    indices = [
        # JuliaModuleIndex,
    ]

    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        # node = nodes.reference('', '', internal=True)
        # node['refid'] = target
        # node['reftitle'] = target
        # node += contnode
        # return node

        scope = node.get('jl:scope')
        # searchmode = node.hasattr('refspecific') and 1 or 0
        matches = self.find_obj(env, modname, clsname, target,
                                type, searchmode)
        if not matches:
            return None
        elif len(matches) > 1:
            env.warn_node(
                'more than one target found for cross-reference '
                '%r: %s' % (target, ', '.join(match[0] for match in matches)),
                node)
        name, obj = matches[0]

        if obj[1] == 'module':
            return self._make_module_refnode(builder, fromdocname, name,
                                             contnode)
        else:
            return make_refnode(builder, fromdocname, obj[0], name,
                                contnode, name)


def update_builder(app):
    #app.warn(str(parser))
    app.env.juliaparser = modelparser.JuliaParser()
    app.env.ref_context["jl:scope"] = []
    # translator = app.builder.translator_class
    # translator.first_kwordparam = True
    # _visit_desc_parameterlist = translator.visit_desc_parameterlist
    # def visit_desc_parameterlist(self, node):
    #     self.first_kwordparam = True
    #     _visit_desc_parameterlist(self, node)
    # translator.visit_desc_parameterlist = visit_desc_parameterlist


def setup(app):
    # app.add_config_value('julia_signature_show_qualifier', True, 'html')
    # app.add_config_value('julia_signature_show_type', True, 'html')
    # app.add_config_value('julia_signature_show_default', True, 'html')
    # app.add_config_value('julia_docstring_show_type', True, 'html')

    for name in ["Module", "AbstractType", "CompositeType", "Function"]:
        translator = translators.TranslatorFunctions[name]
        modelclass = getattr(model, name)
        app.add_node(modelclass,
                     html=translator
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
