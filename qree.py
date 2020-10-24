"""
Qree: Tiny but mighty Python templating.
Copyright (c) 2020 Polydojo, Inc.
""";

import functools;

__version__ = "0.0.2";  # Req'd by flit.
__DEFAULT_TAG_MAP__ = { "@=": "@=",  "@{": "@{",  "@}": "@}",
    "{{:": "{{:",  ":}}": ":}}",  "{{=": "{{=",  "=}}": "=}}",
};
escapeHtml = lambda s: (str(s).replace("&", "&amp;").replace("<", "&lt;")
    .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#x27;")          # TODO: Consider: .replace("`", "&#x60;")
);

def dictDefaults (dicty, defaults):
    "Fills-in missing keys in `dicty` with those from `defaults`.";
    for k in defaults:
        if k not in dicty:
            dicty[k] = defaults[k];
    return dicty;

def roughValidateTagPair (tplStr, opTag, clTag):
    "Helper for roughly validating that tag-counts match.";
    if tplStr.count(opTag) != tplStr.count(clTag):
        raise SyntaxError("Template Error:: Tag-count mismatch for tags `%s` and `%s`." % (opTag, clTag));
    return True;

def roughValidateTplStr (tplStr, tagMap):
    "Helper for roughly validating `tplStr` formatting.";
    if "'''" in tplStr:
        raise SyntaxError("Template Error:: Can't use 3 consecutive single quotes (''').");
    assert roughValidateTagPair(tplStr, tagMap["@{"], tagMap["@}"]);
    assert roughValidateTagPair(tplStr, tagMap["{{:"], tagMap[":}}"]);
    assert roughValidateTagPair(tplStr, tagMap["{{="], tagMap["=}}"]);
    return True;

def quoteReplace (tplStr, variable="data", tagMap=None):
    "Returns as string, the function-equivalent of `tplStr`.";
    tagMap = dictDefaults(tagMap or {}, __DEFAULT_TAG_MAP__);
    assert roughValidateTplStr(tplStr, tagMap);
    fnStr = "def templateFn (%s):\n" % variable;
    indentVal = 4;
    indentify = lambda: " " * indentVal;
    fnStr += indentify() + "from qree import escapeHtml as __qree__esc__html__;\n";
    fnStr += indentify() + "output = '';\n";
    for line in tplStr.splitlines(True):
        lx = line.lstrip();
        if lx.startswith(tagMap["@="]):
            fnStr += indentify() + lx[2:].strip() + "\n";
        elif lx.startswith(tagMap["@{"]):
            indentVal += 4;
        elif lx.startswith(tagMap["@}"]):
            indentVal -= 4;
        else:
            fnStr += indentify() + "output += " + "'''" +  (line
                .replace(tagMap["{{="],  "''' + str(")
                .replace(tagMap["=}}"],  ") + '''")
                .replace(tagMap["{{:"],  "''' + __qree__esc__html__(")
                .replace(tagMap[":}}"],  ") + '''")
            ) + "''';\n";
    fnStr += indentify() + "return output;\n";
    return fnStr;

def execEval (fnStr):
    "Converts `fnStr` to a callable function and returns it.";
    exec(fnStr); # Via exec(), 'templateFn' has been defined.
    return eval("templateFn");

def renderStr (tplStr, data=None, variable="data", tagMap=None):
    "Render template `tplStr` using `data`.";
    fnStr = quoteReplace(tplStr, variable, tagMap);
    fn = execEval(fnStr);
    return fn(data);

def renderPath (tplPath, data=None, variable="data", tagMap=None):
    "Render template at path `tplPath` using `data`.";
    with open(tplPath, "r") as f:
        return renderStr(f.read(), data, variable, tagMap);

def view (tplPath, variable="data", tagMap=None):
    "Returns a decorator for binding function to template at `tplPath`.";
    def decorator (fn):
        @functools.wraps(fn)
        def wrapper (*a, **ka):
            return renderPath(tplPath, fn(*a, **ka), variable, tagMap);
        return wrapper;
    return decorator;

#TODO:
#checkNonPathy = lambda s: "\n" in s or "{" in s or "@" in s;
#def render (s, data=None, variable="data", tagMap=None):
#    "Wr";
#    renderFn = renderStr if checkNonPathy(s) else renderPath;
#    return renderFn(s, data, variable, tagMap);

# End ######################################################
