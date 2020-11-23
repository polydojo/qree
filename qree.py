"""
Qree: Tiny but mighty Python templating.

Copyright (c) 2020 Polydojo, Inc.

SOFTWARE LICENSING
------------------
The software is released "AS IS" under the MIT License,
WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. Kindly
see LICENSE.txt for more details.

NO TRADEMARK RIGHTS
-------------------
The above software licensing terms DO NOT grant any right in the
trademarks, service marks, brand names or logos of Polydojo, Inc.
""";

import functools;

__version__ = "0.0.3";  # Req'd by flit.
__DEFAULT_TAG_MAP__ = { "@=": "@=",  "@{": "@{",  "@}": "@}",
    "{{:": "{{:",  ":}}": ":}}",  "{{=": "{{=",  "=}}": "=}}",
};

escHtml = lambda s: (str(s).replace("&", "&amp;").replace("<", "&lt;")
    .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#x27;")          # TODO: Consider: .replace("`", "&#x60;")
);

def dictDefaults (dicty, defaults):
    "Fills-in missing keys in `dicty` with those from `defaults`.";
    for k in defaults:
        if k not in dicty:
            dicty[k] = defaults[k];
    return dicty;

def findFirstMatch(haystack, needleList, fromIndex=0):
    "Finds needle in `haystack from needlList w/ lowest index.";
    foundNeedle = None;
    minIndex = None;
    for needle in needleList:
        index = haystack.find(needle, fromIndex);
        if index == -1:
            pass;
        elif (minIndex is None) or (index < minIndex):
            foundNeedle = needle;
            minIndex = index;
    return (foundNeedle, minIndex);

def validateSubstitutionTagPair (opTag, clTag, tagMap):
    "Helps escapeNonPyQuotes().";
    assert opTag in [tagMap["{{="], tagMap["{{:"]];
    expectedClTag = tagMap["=}}" if opTag == tagMap["{{="] else ":}}"];
    if clTag != expectedClTag:
        raise SyntaxError("Tag-mismatch. Expected %r, not %r" % (
            expectedClTag, clTag,
        ));
    # otherwise ...
    return True;

def escapeNonPyQuotes (line, tagMap):
    tags = list(map(tagMap.get, "{{= =}} {{: :}}".split()));
    firstTag, firstIndex = findFirstMatch(line, tags);
    if not firstTag:
        return line.replace("'", r"\'");
    # otherwise ...
    nextTag, nextIndex = findFirstMatch(line, tags, firstIndex+1);
    assert validateSubstitutionTagPair(firstTag, nextTag, tagMap);
    beyondNextTagEndIndex = nextIndex + len(nextTag);
    return (
        line[ : firstIndex].replace("'", r"\'") +
        line[firstIndex: beyondNextTagEndIndex] +
        escapeNonPyQuotes(line[beyondNextTagEndIndex : ], tagMap) #+
    );

def validateStandaloneIndentLine (line, tag):
    "Ensures indent-line only has indent-tag, excl. comment.";
    if line.split("#")[0].strip() != tag:
        raise IndentationError("Invalid de/indent line: %r" % line);
    return True;

def quoteReplace (tplStr, variable="data", tagMap=None):
    "Returns as string, the function-equivalent of `tplStr`.";
    tagMap = dictDefaults(tagMap or {}, __DEFAULT_TAG_MAP__);
    fnStr = "def templateFn (%s):\n" % variable;
    innerIndentDepth = 0;   # Depth due to @{ and @} only.
    indentify = lambda: " " * ((1 + innerIndentDepth) * 4);
    fnStr += indentify() + "from qree import escHtml as __qreeEsc;\n";
    fnStr += indentify() + "output = '';\n";
    for line in tplStr.splitlines(True):
        # Param `keepends=True` ^^^^. (Not kwarg for py2.)
        lx = line.lstrip();
        if lx.startswith(tagMap["@="]):
            pyCode = lx[len(tagMap["@="]) : ].strip();
            fnStr += indentify() + pyCode + "\n";
        elif lx.startswith(tagMap["@{"]):
            assert validateStandaloneIndentLine(lx, tagMap["@{"])
            innerIndentDepth += 1;
        elif lx.startswith(tagMap["@}"]):
            assert validateStandaloneIndentLine(lx, tagMap["@}"])
            innerIndentDepth -= 1;
        else:
            
            fnStr += indentify() + "output += " + "'''" +  (
                escapeNonPyQuotes(line, tagMap) # <- Err thrower
                    .replace(tagMap["{{="],  "''' + str(")
                    .replace(tagMap["=}}"],  ") + '''")
                    .replace(tagMap["{{:"],  "''' + __qreeEsc(")
                    .replace(tagMap[":}}"],  ") + '''")
            ) + "''';\n";
    fnStr += indentify() + "return output;\n";
    if innerIndentDepth != 0:
        raise IndentationError("Tag-mismatch for tags " +
            ("%r and %r." % (tagMap["@{"], tagMap["@}"])) #+
        );
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

# TODO/Consider:
#checkNonPathy = lambda s: "\n" in s or "{" in s or "@" in s;
#def render (s, data=None, variable="data", tagMap=None):
#    "Wrapper that auto-picks renderPath() or renderStr()";
#    renderFn = renderStr if checkNonPathy(s) else renderPath;
#    return renderFn(s, data, variable, tagMap);

# End ######################################################
