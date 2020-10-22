# Qree 0.0.1-dev
# Copyright (c) 2020 Polydojo, Inc.
# Qree may be freely distributed under the MIT license.

"""
Qree (read 'curry') is a tiny but mighty templating engine.
The name 'Qree' is short for: Quote, replace, exec(), eval().

Instead of using regular expressions or complex grammars,
Qree uses Python's exec() & eval() for all the heavy lifting.

Inspired by the _.template() function in Underscore.js, Qree
is under 100 lines of code, including docstrings & comments!
""";

import os;

def escapeHtml (s):
    "Simple HTML escaper.";
    return (str(s).replace("&", "&amp;")
        .replace("<", "&lt;").replace(">", "&gt;")
        .replace('"', "&quot;").replace("'", "&#x27;")
        .replace("`", "&#x60;")
    );

def dictDefaults (dicty, defaults):
    "Fills-in missing keys in `dicty` with those from `defaults`.";
    for k in defaults:
        if k not in dicty:
            dicty[k] = defaults[k];
    return dicty;

def quoteReplace (tplStr,   variable  ="data", tagMap=None):
    "Returns as a string, the equivalent function body for `tplStr`.";
    tagMap = dictDefaults(tagMap or {}, {
        "@=": "@=",  "@{": "@{",  "@}": "@}",
        "{{:": "{{:",  ":}}": ":}}",  "{{=": "{{=",  "=}}": "=}}",
    });
    if "'''" in tplStr:
        raise SyntaxError("Can't use 3 consecutive single quotes (''').");
    fnStr = "def templateFn (%s):\n" %   variable  ;
    indentVal = 4;
    indentify = lambda: " " * indentVal;
    fnStr += indentify() + "from qree import escapeHtml as __qree__esc__html__;\n";
    fnStr += indentify() + "output = '';\n";
    lines = tplStr.split("\n");
    for lineIndex in range(len(lines)):
        line = lines[lineIndex];
        lx = line.lstrip();
        if lx.startswith(tagMap["@="]):
            fnStr += indentify() + lx[2:].strip() + "\n";
        elif lx.startswith(tagMap["@{"]):
            fnStr += "\n";
            indentVal += 4;
        elif lx.startswith(tagMap["@}"]):
            indentVal -= 4;
        else:
            tailN = "\\n" if lineIndex != len(lines) - 1 else "";
            fnStr += indentify() + "output += " + "'''" +  (line
                .replace(tagMap["{{:"],  "''' + __qree__esc__html__(")
                .replace(tagMap[":}}"],  ") + '''")
                .replace(tagMap["{{="],  "''' + str(")
                .replace(tagMap["=}}"],  ") + '''")
            ) + "%s''';\n" % tailN; 
    fnStr += indentify() + "return output;\n";
    return fnStr;

def execEval (fnStr):
    "Thin wrapper around Python's exec() and eval().";
    exec(fnStr); # Via exec(), 'templateFn' has been defined.
    return eval("templateFn");

def renderStr (tplStr, data=None,   variable  ="data", tagMap=None):
    "Render template string `tplStr` using `data`.";
    fnStr = quoteReplace(tplStr,   variable  , tagMap);
    fn = execEval(fnStr);
    return fn(data);

def renderPath(tplPath, data=None,   variable  ="data", tagMap=None):
    "Render template at path `tplPath` using `data`.";
    with open(tplPath, "r") as f:
        return renderStr(f.read(), data,   variable  , tagMap);
