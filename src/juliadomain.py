# -*- coding: utf-8 -*-
"""
    sphinx.domains.julia
    ~~~~~~~~~~~~~~~~~~~~

    The Julia domain.

    :copyright: Copyright 2015 by Sebastian Krämer
    :license: BSD, see LICENSE for details.
"""

import re

import docutils
from docutils import nodes
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import make_refnode
from sphinx.util.compat import Directive
from sphinx.util.docfields import Field, GroupedField, TypedField


# REs for Julia signatures
julia_signature_regex = re.compile(
    r'''^ (?P<qualifiers>[\w.]*\.)?
          (?P<name>\w+)  \s*
          (?: \{(?P<templateparameters>.*)\})?
          (?: \((?P<arguments>.*)\)
          )? $
          ''', re.VERBOSE)


class desc_keyparameter(nodes.Part, nodes.Inline, nodes.TextElement):
    """Node for a key parameter."""


def _iteritems(d):
    for k in d:
        yield k, d[k]


def parsearguments(signode, arguments):
    """
    "Parse" a list of arguments separated by commas.

    Arguments can have "optional" annotations given by enclosing them in
    brackets.  Currently, this will split at any comma, even if it's inside a
    string literal (e.g. default argument value).
    """
    paramlist = addnodes.desc_parameterlist()
    a = arguments.split(";")
    args = a[0].split(",")
    if len(a) == 1:
        kwargs = []
    elif len(a) == 2:
        kwargs = a[1].split(",")
    else:
        raise ValueError()
    for arg in args:
        x = arg.strip()
        paramlist += addnodes.desc_parameter(x, x)
    for arg in kwargs:
        x = arg.strip()
        paramlist += desc_keyparameter(x, x)
    # paramlist += addnodes.desc_parameter(kwargs, kwargs)
    signode += paramlist


class JuliaObject(ObjectDescription):
    """
    Description of a general Julia object.
    """
    option_spec = {
        'noindex': directives.flag,
        'module': directives.unchanged,
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
        TypedField('variable', label=l_('Variables'), rolename='obj',
                   names=('var', 'ivar', 'cvar'),
                   typerolename='obj', typenames=('vartype',),
                   can_collapse=True),
        GroupedField('exceptions', label=l_('Raises'), rolename='exc',
                     names=('raises', 'raise', 'exception', 'except'),
                     can_collapse=True),
        Field('returnvalue', label=l_('Returns'), has_arg=False,
              names=('returns', 'return')),
        Field('returntype', label=l_('Return type'), has_arg=False,
              names=('rtype',), bodyrolename='obj'),
    ]

    def get_signature_prefix(self, sig):
        """
        May return a prefix to put before the object name in the signature.
        """
        return ''

    def needs_arglist(self):
        """
        May return true if an empty argument list is to be generated even if
        the document contains none.
        """
        return False

    def handle_signature(self, sig, signode):
        """
        Transform a Julia signature into RST nodes.
        Returns (fully qualified name of the thing, classname if any).

        If inside a class, the current class name is handled intelligently:
        * it is stripped from the displayed name if present
        * it is added to the full name (return value) if not present
        """
        m = julia_signature_regex.match(sig)
        if m is None:
            raise ValueError
        d = m.groupdict()
        qualifiers = d.get("qualifiers", "")
        name = d["name"]
        templateparameters = d.get("templateparameters", "")
        arguments = d.get("arguments", "")

        # determine module and class name (if applicable), as well as full name
        modname = self.options.get(
            'module', self.env.temp_data.get('jl:module'))

        if qualifiers:
            fullname = qualifiers + name
        else:
            fullname = name

        if templateparameters:
            fullname += "{" + templateparameters + "}"

        signode['module'] = modname
        signode['fullname'] = fullname

        sig_prefix = self.get_signature_prefix(sig)
        if sig_prefix:
            signode += addnodes.desc_annotation(sig_prefix, sig_prefix)

        if qualifiers:
            signode += addnodes.desc_addname(qualifiers, qualifiers)
        # exceptions are a special case, since they are documented in the
        # 'exceptions' module.
        elif self.env.config.add_module_names:
                modname = self.options.get(
                    'module', self.env.temp_data.get('jl:module'))
                if modname:
                    nodetext = modname + "."
                    signode += addnodes.desc_addname(nodetext, nodetext)

        signode += addnodes.desc_name(fullname, fullname)
        if not arguments:
            if self.needs_arglist():
                # for callables, add an empty parameter list
                signode += addnodes.desc_parameterlist()
        else:
            parsearguments(signode, arguments)
        return fullname, qualifiers

    def get_index_text(self, modname, name):
        """
        Return the text for the index entry of the object.
        """
        raise NotImplementedError('must be implemented in subclasses')

    def _is_class_member(self):
        return self.objtype.startswith('attr')

    def add_target_and_index(self, name_cls, sig, signode):
        modname = self.options.get(
            'module', self.env.ref_context.get('jl:module'))
        fullname = (modname and modname + '.' or '') + name_cls[0]
        # note target
        if fullname not in self.state.document.ids:
            signode['names'].append(fullname)
            signode['ids'].append(fullname)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            objects = self.env.domaindata['jl']['objects']
            if fullname in objects:
                self.state_machine.reporter.warning(
                    'duplicate object description of %s, ' % fullname +
                    'other instance in ' +
                    self.env.doc2path(objects[fullname][0]) +
                    ', use :noindex: for one of them',
                    line=self.lineno)
            objects[fullname] = (self.env.docname, self.objtype)

        indextext = self.get_index_text(modname, name_cls)
        if indextext:
            self.indexnode['entries'].append(('single', indextext,
                                              fullname, ''))

    def before_content(self):
        # needed for automatic qualification of members (reset in subclasses)
        self.clsname_set = False

    def after_content(self):
        if self.clsname_set:
            self.env.temp_data['jl:class'] = None


class JuliaFunction(JuliaObject):
    """
    Description of an object on module level (functions, data).
    """

    def needs_arglist(self):
        return self.objtype == 'function'

    def handle_signature(self, sig, signode):
        """
        Transform a Julia signature into RST nodes.
        Returns (fully qualified name of the thing, classname if any).

        If inside a class, the current class name is handled intelligently:
        * it is stripped from the displayed name if present
        * it is added to the full name (return value) if not present
        """
        if sig == "<auto>":
            function = self.funcdict
        else:
            m = julia_signature_regex.match(sig)
            if m is None:
                raise ValueError
            d = m.groupdict()
            qualifiers = d.get("qualifiers", "")
            name = d["name"]
            templateparameters = d.get("templateparameters", "")
            arguments = d.get("arguments", "")
        content = docutils.statemachine.ViewList(function["docstring"].split("\n"))
        self.content = content
        #raise(Exception(self.content.items))

        fullname = function["name"]
        if function["templateparameters"]:
            fullname += "{" + ",".join(function["templateparameters"]) + "}"
        signode['fullname'] = fullname
        signode += addnodes.desc_name(fullname, fullname)
        paramlist = addnodes.desc_parameterlist()
        signode += paramlist
        for arg in function["arguments"]:
            x = arg["name"]
            paramlist += addnodes.desc_parameter(x, x)
        for arg in function["kwarguments"]:
            x = arg["name"]
            paramlist += desc_keyparameter(x, x)
        # raise Exception(self.content.items)
        return fullname


    def get_index_text(self, modname, name_cls):
        if self.objtype == 'function':
            if not modname:
                return _('%s() (built-in function)') % name_cls[0]
            return _('%s() (in module %s)') % (name_cls[0], modname)
        elif self.objtype == 'data':
            if not modname:
                return _('%s (built-in variable)') % name_cls[0]
            return _('%s (in module %s)') % (name_cls[0], modname)
        else:
            return ''


class JuliaModule(Directive):
    """
    Directive to mark description of a new module.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'platform': lambda x: x,
        'synopsis': lambda x: x,
        'noindex': directives.flag,
        'deprecated': directives.flag,
    }

    def run(self):
        env = self.state.document.settings.env
        modname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.ref_context['jl:module'] = modname
        ret = []
        if not noindex:
            env.domaindata['jl']['modules'][modname] = \
                (env.docname, self.options.get('synopsis', ''),
                 self.options.get('platform', ''), 'deprecated' in self.options)
            # make a duplicate entry in 'objects' to facilitate searching for
            # the module in JuliaDomain.find_obj()
            env.domaindata['jl']['objects'][modname] = (env.docname, 'module')
            targetnode = nodes.target('', '', ids=['module-' + modname],
                                      ismod=True)
            self.state.document.note_explicit_target(targetnode)
            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)
            indextext = _('%s (module)') % modname
            inode = addnodes.index(entries=[('single', indextext,
                                             'module-' + modname, '')])
            ret.append(inode)
        return ret


class JuliaClasslike(JuliaObject):
    """
    Description of a class-like object (classes, exceptions).
    """

    def get_signature_prefix(self, sig):
        return self.objtype + ' '

    def get_index_text(self, modname, name_cls):
        if self.objtype == 'class':
            if not modname:
                return _('%s (built-in class)') % name_cls[0]
            return _('%s (class in %s)') % (name_cls[0], modname)
        elif self.objtype == 'exception':
            return name_cls[0]
        else:
            return ''

    def before_content(self):
        JuliaObject.before_content(self)
        if self.names:
            self.env.ref_context['jl:class'] = self.names[0][0]
            self.clsname_set = True


class JuliaAttribute(JuliaObject):
    """
    Description of class attributes.
    """

    def get_index_text(self, modname, name_cls):
        name, cls = name_cls
        add_modules = self.env.config.add_module_names

        try:
            clsname, attrname = name.rsplit('.', 1)
        except ValueError:
            if modname:
                return _('%s (in module %s)') % (name, modname)
            else:
                return name
        if modname and add_modules:
            return _('%s (%s.%s attribute)') % (attrname, modname, clsname)
        else:
            return _('%s (%s attribute)') % (attrname, clsname)

    def before_content(self):
        JuliaObject.before_content(self)
        lastname = self.names and self.names[-1][1]
        if lastname and not self.env.ref_context.get('jl:class'):
            self.env.ref_context['jl:class'] = lastname.strip('.')
            self.clsname_set = True


class JuliaXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        refnode['jl:module'] = env.ref_context.get('jl:module')
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


class JuliaModuleIndex(Index):
    """
    Index subclass to provide the Julia module index.
    """

    name = 'modindex'
    localname = l_('Julia Module Index')
    shortname = l_('modules')

    def generate(self, docnames=None):
        content = {}
        # list of prefixes to ignore
        ignores = self.domain.env.config['modindex_common_prefix']
        ignores = sorted(ignores, key=len, reverse=True)
        # list of all modules, sorted by module name
        modules = sorted(_iteritems(self.domain.data['modules']),
                         key=lambda x: x[0].lower())
        # sort out collapsable modules
        prev_modname = ''
        num_toplevels = 0
        for modname, (docname, synopsis, platforms, deprecated) in modules:
            if docnames and docname not in docnames:
                continue

            for ignore in ignores:
                if modname.startswith(ignore):
                    modname = modname[len(ignore):]
                    stripped = ignore
                    break
            else:
                stripped = ''

            # we stripped the whole module name?
            if not modname:
                modname, stripped = stripped, ''

            entries = content.setdefault(modname[0].lower(), [])

            package = modname.split('::')[0]
            if package != modname:
                # it's a submodule
                if prev_modname == package:
                    # first submodule - make parent a group head
                    entries[-1][1] = 1
                elif not prev_modname.startswith(package):
                    # submodule without parent in list, add dummy entry
                    entries.append([stripped + package, 1, '', '', '', '', ''])
                subtype = 2
            else:
                num_toplevels += 1
                subtype = 0

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([stripped + modname, subtype, docname,
                            'module-' + stripped + modname, platforms,
                            qualifier, synopsis])
            prev_modname = modname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel modules is larger than
        # number of submodules
        collapse = len(modules) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(_iteritems(content))

        return content, collapse


class JuliaDomain(Domain):
    """
    Julia language domain.
    """
    name = 'jl'
    label = 'Julia'
    object_types = {
        'function':        ObjType(l_('function'),         'func', 'obj'),
        # 'global':          ObjType(l_('global variable'),  'global', 'obj'),
        'class':            ObjType(l_('class'),            'class', 'obj'),
        'exception':       ObjType(l_('exception'),        'exc', 'obj'),
        'attribute':       ObjType(l_('attribute'),        'attr', 'obj'),
        # 'const':           ObjType(l_('const'),            'const', 'obj'),
        'module':          ObjType(l_('module'),           'mod', 'obj'),
    }

    directives = {
        'function':        JuliaFunction,
        # 'global':          JuliaGloballevel,
        # 'const':           JuliaEverywhere,
        'class':            JuliaClasslike,
        'exception':       JuliaClasslike,
        'attribute':     JuliaAttribute,
        'module':          JuliaModule,
    }

    roles = {
        'func':   JuliaXRefRole(fix_parens=False),
        # 'global': JuliaXRefRole(),
        'class':  JuliaXRefRole(),
        'exc':    JuliaXRefRole(),
        'attr':   JuliaXRefRole(),
        # 'const':  JuliaXRefRole(),
        'mod':    JuliaXRefRole(),
        'obj':    JuliaXRefRole(),
    }
    initial_data = {
        'objects': {},  # fullname -> docname, objtype
        'modules': {},  # modname -> docname, synopsis, platform, deprecated
    }
    indices = [
        JuliaModuleIndex,
    ]

    def clear_doc(self, docname):
        for fullname, (fn, _) in list(self.data['objects'].items()):
            if fn == docname:
                del self.data['objects'][fullname]
        for modname, (fn, _, _, _) in list(self.data['modules'].items()):
            if fn == docname:
                del self.data['modules'][modname]

    def find_obj(self, env, modname, classname, name, type, searchorder=0):
        """
        Find a Julia object for "name", perhaps using the given module and/or
        classname.
        """
        # skip parens
        if name[-2:] == '()':
            name = name[:-2]

        if not name:
            return None, None

        objects = self.data['objects']

        newname = None
        if searchorder == 1:
            if modname and classname and \
                     modname + '::' + classname + '#' + name in objects:
                newname = modname + '::' + classname + '#' + name
            elif modname and classname and \
                     modname + '::' + classname + '.' + name in objects:
                newname = modname + '::' + classname + '.' + name
            elif modname and modname + '::' + name in objects:
                newname = modname + '::' + name
            elif modname and modname + '#' + name in objects:
                newname = modname + '#' + name
            elif modname and modname + '.' + name in objects:
                newname = modname + '.' + name
            elif classname and classname + '.' + name in objects:
                newname = classname + '.' + name
            elif classname and classname + '#' + name in objects:
                newname = classname + '#' + name
            elif name in objects:
                newname = name
        else:
            if name in objects:
                newname = name
            elif classname and classname + '.' + name in objects:
                newname = classname + '.' + name
            elif classname and classname + '#' + name in objects:
                newname = classname + '#' + name
            elif modname and modname + '::' + name in objects:
                newname = modname + '::' + name
            elif modname and modname + '#' + name in objects:
                newname = modname + '#' + name
            elif modname and modname + '.' + name in objects:
                newname = modname + '.' + name
            elif modname and classname and \
                     modname + '::' + classname + '#' + name in objects:
                newname = modname + '::' + classname + '#' + name
            elif modname and classname and \
                     modname + '::' + classname + '.' + name in objects:
                newname = modname + '::' + classname + '.' + name
            # special case: object methods
            elif type in ('func', 'meth') and '.' not in name and \
                 'object.' + name in objects:
                newname = 'object.' + name
        if newname is None:
            return None, None
        return newname, objects[newname]

    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        if (typ == 'mod' or
            typ == 'obj' and target in self.data['modules']):
            docname, synopsis, platform, deprecated = \
                self.data['modules'].get(target, ('', '', '', ''))
            if not docname:
                return None
            else:
                title = '%s%s%s' % ((platform and '(%s) ' % platform),
                                    synopsis,
                                    (deprecated and ' (deprecated)' or ''))
                return make_refnode(builder, fromdocname, docname,
                                    'module-' + target, contnode, title)
        else:
            modname = node.get('jl:module')
            clsname = node.get('jl:class')
            searchorder = node.hasattr('refspecific') and 1 or 0
            name, obj = self.find_obj(env, modname, clsname,
                                      target, typ, searchorder)
            if not obj:
                return None
            else:
                return make_refnode(builder, fromdocname, obj[0], name,
                                    contnode, name)

    def get_objects(self):
        for modname, info in _iteritems(self.data['modules']):
            yield (modname, modname, 'module', info[0], 'module-' + modname, 0)
        for refname, (docname, type) in _iteritems(self.data['objects']):
            yield (refname, refname, type, docname, refname, 1)


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

import types


def update_builder(app):
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
