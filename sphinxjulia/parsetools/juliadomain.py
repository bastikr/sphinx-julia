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

    def parse_arguments(self):
        raise NotImplementedError()

    def parse_content(self, modelnode):
        self.state.nested_parse(self.content, self.content_offset, modelnode)

    def run(self):
        if ':' in self.name:
            self.domain, self.objtype = self.name.split(':', 1)
        else:
            self.domain, self.objtype = '', self.name
        self.env = self.state.document.settings.env
        modelnode = self.parse_arguments()
        modelnode.setid(self)
        modelnode.register(self.env)
        self.parse_content(modelnode)
        #self.env.domaindata['jl'][type(modelnode)].append(modelnode)
        return [modelnode]


class ModuleDirective(JuliaDirective):

    def parse_arguments(self):
        text = "module " + self.arguments[0] + "\nend"
        m = self.env.juliaparser.parsestring("module", text)
        return m

    def parse_content(self, modelnode):
        self.env.ref_context['jl:scope'].append(modelnode.name)
        JuliaDirective.parse_content(self, modelnode)
        self.env.ref_context['jl:scope'].pop()


class FunctionDirective(JuliaDirective):

    def parse_arguments(self):
        text = "function " + self.arguments[0] + "\nend"
        m = self.env.juliaparser.parsestring("function", text)
        return m


class AbstractTypeDirective(JuliaDirective):

    def parse_arguments(self):
        text = "abstract " + self.arguments[0]
        m = self.env.juliaparser.parsestring("abstracttype", text)
        return m


class CompositeTypeDirective(JuliaDirective):

    def parse_arguments(self):
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
        "module": {}, # uid -> docname
        "function": {}, # (docname, FunctionNode)
        "abstract": {}, # uid -> docname
        "type": {} # uid -> docname
        # 'objects': {},  # fullname -> docname, objtype
        # 'modules': {},  # modname -> docname, synopsis, platform, deprecated
    }
    indices = [
        # JuliaModuleIndex,
    ]

    def find_obj(self, refname, target):
        print(refname)
        print(target)
        for typename, objtype in self.object_types.items():
            if refname in objtype.roles:
                break
        else:
            return []
        print("data", self.initial_data)
        if target in self.initial_data[typename]:
            return [(target, self.initial_data[typename][target])]
        return []


    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        # node = nodes.reference('', '', internal=True)
        # node['refid'] = target
        # node['reftitle'] = target
        # node += contnode
        # return node

        # print('env:' + str(env))
        # print('fromdocname:' + str(fromdocname))
        # print('builder:' + str(builder))
        # print('typ:' + str(typ))
        # print('target:' + str(target))
        # print('node:' + str(node))
        # print('contnode:' + str(contnode))
        # assert False
        matches = self.find_obj(typ, target)
        if not matches:
            return None
        elif len(matches) > 1:
            env.warn_node(
                'more than one target found for cross-reference '
                '%r: %s' % (target, ', '.join(match[0] for match in matches)),
                node)
        name, todocname = matches[0]
        return make_refnode(builder, fromdocname, todocname, target,
                                contnode, target)
        # return make_refnode(builder, fromdocname, obj[0], name,
        #                         contnode, name)


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
    app.connect('builder-inited', update_builder)
    app.add_domain(JuliaDomain)
