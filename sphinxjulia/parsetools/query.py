import docutils.utils

import model
import modelparser


def resolvescope(basescope, targetstring):
    if "." not in targetstring:
        return [], targetstring
    innerscope, name = targetstring.rsplit(".", 1)
    innerscope = innerscope.split(".")
    if innerscope[0] == "":
        return basescope + innerscope[1:], name
    return innerscope, name


def match_argument(pattern, argument):
    if pattern.name and pattern.name != argument.name:
        return False
    if pattern.argumenttype and pattern.argumenttype != argument.argumenttype:
        return False
    if pattern.value and pattern.value != argument.value:
        return False
    return True


def match_signature(pattern, signature):
    parguments = pattern.positionalarguments + pattern.optionalarguments
    farguments = signature.positionalarguments + signature.optionalarguments
    if len(parguments) != len(parguments):
        return False
    for i in range(len(parguments)):
        if not match_argument(parguments[i], farguments[i]):
            return False
    pkwd = {arg.name: arg for arg in pattern.keywordarguments}
    fkwd = {arg.name: arg for arg in signature.keywordarguments}
    for name in pkwd:
        if name not in fkwd or not match_argument(pkwd["name"]):
            return False
    return True


def match_function(pattern, function):
    if pattern.name != function.name:
        return False
    tpars = set(pattern.templateparameters)
    if tpars and tpars != set(function.templateparameters):
        return False
    return match_signature(pattern.signature, function.signature)


def match_module(pattern, module):
    if pattern.name != module.name:
        return False
    return True


def match_type(pattern, type):
    if pattern.name != type.name:
        return False
    return True


def match_abstract(pattern, abstract):
    if pattern.name != abstract.name:
        return False
    return True


def match(pattern, obj):
    if type(pattern) != type(obj):
        return False
    f = eval("match_"+type(obj).__name__.lower())
    return f(pattern, obj)


def find_function_by_string(basescope, targetstring, dictionary):
    funcpattern = modelparser.parse_functionstring(targetstring)
    if funcpattern.modulename:
        name = ".".join([funcpattern.modulename, funcpattern.name])
    else:
        name = funcpattern.name
    refscope, name = resolvescope(basescope, name)
    if name not in dictionary:
        return []
    tpars = set(funcpattern.templateparameters)
    matches = []
    for func in dictionary[name]:
        if len(refscope)!=0 and refscope != func["scope"]:
            continue
        if tpars and tpars != set(func.templateparameters):
            continue
        if match_signature(funcpattern.signature, func["signature"]):
            matches.append(func)
    return matches


def find_object_by_string(objtype, basescope, targetstring, dictionaries):
    dictionary = dictionaries[objtype]
    if objtype == "function":
        return find_function_by_string(basescope, targetstring, dictionary)
    refscope, name = resolvescope(basescope, targetstring)
    if name not in dictionary:
        return []
    matches = []
    for obj in dictionary[name]:
        if len(refscope)==0 or refscope == obj["scope"]:
            matches.append(obj)
    return matches


class NodeWalker:

    def __init__(self, scope, document, callback):
        self.scope = scope
        self.document = document
        self.callback = callback

    def dispatch_visit(self, node):
        if isinstance(node, model.JuliaModelNode):
            if self.scope and self.scope[0] == "":
                scope = self.scope[1:]
            else:
                scope = self.scope
            self.callback(node, scope)

        if isinstance(node, model.Module):
            self.scope.append(node.name)

    def dispatch_departure(self, node):
        if isinstance(node, model.Module):
            self.scope.pop()


def walk_tree(node, callback, scope):
    document = docutils.utils.new_document("")
    walker = NodeWalker(scope, document, callback)
    node.walkabout(walker)
