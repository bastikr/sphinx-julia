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
    final_argument_whitespace = False
    nodeclass = None

    def run(self):
        if ':' in self.name:
            self.domain, self.objtype = self.name.split(':', 1)
        else:
            self.domain, self.objtype = '', self.name
        self.env = self.state.document.settings.env
        modelnode = self.parse_arguments()
        self.parse_content(modelnode)
        return [modelnode]

    def parse_arguments(self):
        modelnode = self.nodeclass(name=self.arguments[0])
        modelnode["ids"] = [modelnode.uid(self.env)]
        modelnode.register(self.env)
        return modelnode

    def parse_content(self, modelnode):
        self.state.nested_parse(self.content, self.content_offset, modelnode)


class ModuleDirective(JuliaDirective):
    nodeclass = model.Module

    def parse_content(self, modelnode):
        self.env.ref_context['jl:scope'].append(modelnode.name)
        JuliaDirective.parse_content(self, modelnode)
        self.env.ref_context['jl:scope'].pop()


class FunctionDirective(JuliaDirective):
    nodeclass = model.Function
    final_argument_whitespace = True

    def parse_arguments(self):
        d = modelparser.parse_functionstring(self.arguments[0])
        modelnode = self.nodeclass(**d)
        modelnode["ids"] = [modelnode.uid(self.env)]
        modelnode.register(self.env)
        return modelnode


class AbstractTypeDirective(JuliaDirective):
    nodeclass = model.Abstract


class TypeDirective(JuliaDirective):
    nodeclass = model.Type


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
        'type': TypeDirective,
        'module': ModuleDirective,
    }

    roles = {
        'func': JuliaXRefRole(fix_parens=False),
        'type':  JuliaXRefRole(),
        'abstract': JuliaXRefRole(),
        'mod':    JuliaXRefRole(),
    }

    initial_data = {
        # name -> [{docname, scope, uid}, ...]
        "module": {},
        "abstract": {},
        "type": {},
        # name -> [{docname, scope, templateparameters, signature, uid}]
        "function": {},
    }
    indices = [
        # JuliaModuleIndex,
    ]

    def resolvescope(self, basescope, targetstring):
        if "." not in targetstring:
            return [], targetstring
        innerscope, name = targetstring.rsplit(".", 1)
        innerscope = innerscope.split(".")
        if innerscope[0] == "":
            return basescope + innerscope[1:], name
        return innerscope, name

    def match_argument(self, pattern, argument):
        if pattern.name and pattern.name != argument.name:
            return False
        if pattern.argumenttype and pattern.argumenttype != argument.argumenttype:
            return False
        if pattern.value and pattern.value != argument.value:
            return False
        return True

    def match_signature(self, pattern, function):
        parguments = pattern.positionalarguments + pattern.optionalarguments
        farguments = function.positionalarguments + function.optionalarguments
        if len(parguments) != len(parguments):
            return False
        for i in range(len(parguments)):
            if not self.match_argument(parguments[i], farguments[i]):
                return False
        pkwd = {arg.name: arg for arg in pattern.keywordarguments}
        fkwd = {arg.name: arg for arg in function.keywordarguments}
        for name in pkwd:
            if name not in fkwd or not match_argument(pkwd["name"]):
                return False
        return True

    def find_function(self, node, targetstring):
        basescope = node['jl:scope']
        d = modelparser.parse_functionstring(targetstring)
        name = ".".join([d["modulename"], d["name"]])
        refscope, name = self.resolvescope(basescope, name)
        if name not in self.initial_data["function"]:
            return []
        tpars = set(d["templateparameters"])
        matches = []
        for func in self.initial_data["function"][name]:
            if refscope != func["scope"]:
                continue
            if tpars and tpars != set(func.templateparameters):
                continue
            if self.match_signature(d["signature"], func["signature"]):
                matches.append(func)
        return matches

    def find_obj(self, rolename, node, targetstring):
        for typename, objtype in self.object_types.items():
            if rolename in objtype.roles:
                break
        else:
            return []
        if typename == "function":
            return self.find_function(node, targetstring)
        basescope = node['jl:scope']
        refscope, name = self.resolvescope(basescope, targetstring)
        if name not in self.initial_data[typename]:
            return []
        matches = []
        for obj in self.initial_data[typename][name]:
            if refscope == obj["scope"]:
                matches.append(obj)
        return matches


    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        matches = self.find_obj(typ, node, target)
        if not matches:
            return None
        elif len(matches) > 1:
            env.warn_node(
                'more than one target found for cross-reference '
                '%r: %s' % (target, ', '.join(match[0] for match in matches)),
                node)
        t = matches[0]
        return make_refnode(builder, fromdocname, t["docname"], t["uid"],
                                contnode, target)


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

    for name in ["Module", "Abstract", "Type", "Function"]:
        translator = translators.TranslatorFunctions[name]
        modelclass = getattr(model, name)
        app.add_node(modelclass,
                     html=translator
                     )
    app.connect('builder-inited', update_builder)
    app.add_domain(JuliaDomain)
