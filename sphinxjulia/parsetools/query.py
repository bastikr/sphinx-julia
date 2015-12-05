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
    tpars = set(pattern["templateparameters"])
    if tpars and tpars != set(function.templateparameters):
        return False
    return match_signature(pattern.signature, function.signature)


def find_function_by_string(basescope, targetstring, dictionary):
    d = modelparser.parse_functionstring(targetstring)
    print("d: ", d)
    print("dictionary: ", dictionary)
    if "modulename" in d:
        name = ".".join([d["modulename"], d["name"]])
    else:
        name = d["name"]
    refscope, name = resolvescope(basescope, name)
    if name not in dictionary:
        return []
    tpars = set(d["templateparameters"])
    matches = []
    for func in dictionary[name]:
        if refscope != func["scope"]:
            print("scopes different: ", refscope, func["scope"])
            continue
        if tpars and tpars != set(func.templateparameters):
            continue
        if match_signature(d["signature"], func["signature"]):
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
        if refscope == obj["scope"]:
            matches.append(obj)
    return matches


class Catalog(dict):

    def __init__(self, scope, docname, document, dictionaries):
        self["module"] = {}
        self["abstract"] = {}
        self["type"] = {}
        self["function"] = {}
        self.update(dictionaries)
        self.scope = scope
        self.docname = docname
        self.document = document

    def dispatch_visit(self, node):
        if isinstance(node, model.JuliaModelNode):
            identifier = node.__class__.__name__.lower()
            if self.scope and self.scope[0] == "":
                scope = self.scope[1:]
            else:
                scope = self.scope
            node["ids"] = [node.uid(scope)]
            node.register(self.docname, scope, self[identifier])
        if isinstance(node, model.Module):
            self.scope.append(node.name)

    def dispatch_departure(self, node):
        if isinstance(node, model.Module):
            self.scope.pop()


def catalog_tree(node, scope, docname="", dictionaries=None):
    document = docutils.utils.new_document("")
    if dictionaries is None:
        dictionaries = {}
    c = Catalog(scope, docname, document, dictionaries)
    node.walkabout(c)
    return c
