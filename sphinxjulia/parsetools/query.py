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
    tpars = set(d["templateparameters"])
    if tpars and tpars != set(func.templateparameters):
        return False
    return match_signature(pattern.signature, function.signature)


def find_function_by_string(basescope, targetstring, dictionary):
    d = modelparser.parse_functionstring(targetstring)
    name = ".".join([d["modulename"], d["name"]])
    refscope, name = resolvescope(basescope, name)
    if name not in dictionary:
        return []
    tpars = set(d["templateparameters"])
    matches = []
    for func in dictionary[name]:
        if refscope != func["scope"]:
            continue
        if tpars and tpars != set(func.templateparameters):
            continue
        if match_signature(d["signature"], func["signature"]):
            matches.append(func)
    return matches


def find_object_by_string(basescope, targetstring, dictionary):
    refscope, name = self.resolvescope(basescope, targetstring)
    if name not in dictionary[typename]:
        return []
    matches = []
    for obj in dictionary[name]:
        if refscope == obj["scope"]:
            matches.append(obj)
    return matches
