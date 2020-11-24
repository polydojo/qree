Qree
====

Qree (read 'Curie') is a tiny but mighty Python templating engine, geared toward HTML. 'Qree' is short for: *Q*uote, *r*eplace, *e*xec(), *e*val().

The entire module is under 200 lines. Instead of using regular expressions or PEGs, Qree relies on Python's `exec()` and `eval()`. Thus, it supports *all language features*, out of the box. For more on Qree's internals, please see: [*Build Your Own Python Template Engine*](https://www.sumukhbarve.com/build-python-template-engine)

**!!! Warning:** Do **NOT** render untrusted templates. As Qree uses `eval()`, rendering untrusted templates is equivalent to giving untrusted entities access to your entire systems.

Installation
--------------
```
pip install qree
```
Alternatively, just download `qree.py` into your project directory.

Text Interpolation
----------------------
Use `{{: expression :}}` for HTML-escaped interpolation, or `{{= expression =}}` for interpolation *without* escaping. The latter is *susceptible to XSS*, so please be careful. Here are a few quick examples:

**1. Hello, World!:**
```py
qree.renderStr("<h2>Hello, {{: data :}}", data="World!")
# Output: <h2>Hello, World!</h2>
```

**2. Using Expressions:**
```py
qree.renderStr("<h2>Mr. {{: data.title() + '!' :}}", data="bond")
# Output: <h2>Mr. Bond!</h2>
```

**3.  HTML Escaping:**
```py
qree.renderStr("Mr. {{: data :}}", data="<b> Villain </b>")
# Output: Mr. &lt;b&gt; Villain &lt;/b&gt;
```

**4. Without Escaping:**
```py
qree.renderStr("Mr. {{= data =}}", data="<b> Villain </b>")
# Output: Mr. <b> Villain </b>
```

**5. Longer Example:**
```py
qree.renderStr("""
<!doctype html>
<html>
<head>
    <title>{{: data["title"].title() :}}</title>
</head>
<body>
    <h1>{{: data["title"].title() :}}</h1>
    <pre>{{: data["body"] :}}</pre>
</body>
</html>
""", data={
    "title": "Lorem Ipsum",
    "body": "Lorem ipsum dolor sit amet, ... elit.",
})
```
\# Output:
```html
<!doctype html>
<html>
<head>
    <title>Lorem Ipsum</title>
</head>
<body>
    <h1>Lorem Ipsum</h1>
    <pre>Lorem ipsum dolor sit amet, ... elit.</pre>
</body>
</html>

```

Python Code
----------------
Any line beginning with `@=` is treated as Python code. (Preceding whitespace is ignored.)  You can write **any code** you wish, as Qree supports all language features. You can define variables, import modules, make assertions etc. For example:

**Leap Year Detection (with `lambda`):**
```py
tplStr = """
@= isLeap = lambda n: (n % 400 == 0) or (n % 100 != 0 and n % 4 == 0)
@= isOrIsNot = "IS" if isLeap(data['year']) else "is NOT"
The year {{: data['year'] :}} {{: isOrIsNot :}} a leap year.
"""
qree.renderStr(tplStr, data={"year": 2000})
# Output: The year 2000 IS a leap year.

qree.renderStr(tplStr, data={"year": 2001})
# Output: The year 2001 is NOT a leap year.
```

Python Indentation
------------------------

Python is an indented language. Use the special tags `@{` and `@}` for respectively indicating indentation and de-indentation to Qree. When used, such a tag *should appear by itself on a separate line*, ignoring whitespace and trailing Python comments. For example:

**Leap Year Detection (with `def`):**  
```py
tplStr = """
@= def isLeap (n):
@{
    @= if n % 400 == 0: return True;
    @= if n % 100 == 0: return False;
    @= return n % 4 == 0;
@}
@= isOrIsNot = "IS" if isLeap(data['year']) else "is NOT"
The year {{: data['year'] :}} {{: isOrIsNot :}} a leap year.
"""
qree.renderStr(tplStr, data={"year": 2000})
# Output: The year 2000 IS a leap year.

qree.renderStr(tplStr, data={"year": 2001})
# Output: The year 2001 is NOT a leap year.
```

**FizzBuzz Example**  
FizzBuzz is a popular programming assignment. The idea is to print consecutive numbers per line, but instead to print `'Fizz'` for multiples of 3, `'Buzz'` for multiples of 5, and `'FizzBuzz'` for multiples of 3 and 5.

```py
qree.renderStr("""
@= for n in range(1, data+1):
@{
    @= if n % 15 == 0:
    @{
        FizzBuzz
    @}
    @= elif n % 3 == 0:
    @{
        Fizz
    @}
    @= elif n % 5 == 0:
    @{
        Buzz
    @}
    @= else:
    @{
        {{: n :}}
    @}
@}
""", data=20)
```
\# Output:
```
        1
        2
        Fizz
        4
        Buzz
        Fizz
        7
        8
        Fizz
        Buzz
        11
        Fizz
        13
        14
        FizzBuzz
        16
        17
        Fizz
        19
        Buzz

```

The `data` Variable
-------------------------
By default, data passed via the `data` parameter is available in the template as the `data` variable. However, if you'd like to change the variable name, you may do so via the `variable` parameter. For example:
```py
qree.renderStr("Hi {{: name :}}!", data="Jim", variable="name")
# Output: Hi Jim!
```

Template Files
------------------
It's always convenient to store templates using separate files. To work with files, use `qree.renderPath(tplPath, data, ...)` instead of `qree.renderStr(tplStr, data, ...)`. 

Let's say you have the following directory structure:
```
- app.py
- qree.py
- views/
        - homepage.html
```
Here's `homepage.html` :
```html
<doctype html>
<html>
<head><title>{{: data['title'] :}}</title></head>
<body>
    <h2>{{: data['title'] :}}</h2>
    <pre>{{: data['body'] :}}</pre>
</body>
<html>
```

In `app.py`, you could have the following snippet:
```py
def serve_homepage ():
    return qree.renderPath("./views/homepage.html", data={
        "title": "The TITLE Goes Here!",
        "body": "And the body goes here ...",
    });
```
Which would be equivalent to:
```py
def serve_homepage ():
    with open("./views/homepage.html", "r") as f:
        return qree.renderStr(f.read(), data={
            "title": "The TITLE Goes Here!",
            "body": "And the body goes here ...",
        });
```
In either case, the output would be:
```html
<doctype html>
<html>
<head><title>The TITLE Goes Here!</title></head>
<body>
<h2>The TITLE Goes Here!</h2>
<pre>And the body goes here ...</pre>
</body>
<html>

```

Quick Plug
--------------
Qree built and maintained by the folks at [Polydojo, Inc.](https://www.polydojo.com/), led by [Sumukh Barve](https://www.sumukhbarve.com/). If your team is looking for a simple project management tool, please check out our latest product: [**BoardBell.com**](https://www.boardbell.com/).

Template Nesting
----------------------
Since templates can include any Python code, you can call `qree.renderPath()` from within a template! Consider the following directory structure:
```
- app.py
- qree.py
- views/
        - header.html
        - homepage.html
        - footer.html
```
With `header.html`:
```html
<header class="header">
    <a href="/link1">Link 1</a>
    <a href="/link2">Link 2</a>
    <a href="/link3">Link 3</a>
</header>
```

And similarly, `footer.html`:
```html
<footer class="footer">
    <a href="/linkA">Link A</a>
    <a href="/linkB">Link B</a>
    <a href="/linkC">Link C</a>
</footer>
```

Now, you can use `header.html` and `footer.html` in `homepage.html`:
```html
@= import qree;
@= import qree;
<doctype html>
<html>
<head><title>{{: data['title'] :}}</title></head>
<body>
{{= qree.renderPath("./test-views/header.html", data=None) =}}
<h2>{{: data['title'] :}}</h2>
<pre>{{: data['body'] :}}</pre>
{{= qree.renderPath("./test-views/footer.html", data=None) =}}
</body>
<html>
```

And, as before, the snippet in `app.py`:
```py
def serve_homepage ():
    return qree.renderPath("./views/homepage.html", data={
        "title": "The TITLE Goes Here!",
        "body": "And the body goes here ...",
    });
```
The output is:
```html
<doctype html>
<html>
<head><title>... TITLE 2 ...</title></head>
<body>
<header class="header">
    <a href="/link1">Link 1</a>
    <a href="/link2">Link 2</a>
    <a href="/link3">Link 3</a>
</header>

<h2>... TITLE 2 ...</h2>
<pre>... BODY 2 ...</pre>
<footer class="footer">
    <a href="/linkA">Link A</a>
    <a href="/linkB">Link B</a>
    <a href="/linkC">Link C</a>
</footer>

</body>
<html>

```

In the above example, we explicitly passed `data=None` to each nested template. We could've passed any value. We could've even ignored the `data` parameter, as it defaults to `None` anyway.


Custom Tags (via `tagMap`)
---------------------------------

Default tags like `{{:`, `:}}`, `@=`, etc. can each be customized via the `tagMap` parameter. Using `tagMap`, just supply your desired tag as the value against the default tag as key. A few examples follow:

**1. `[[:` Square `:]]` Brackets Instead Of `{{:` Braces `:}}`**
```py
qree.renderStr(
    tplStr="Hello, [[: data.title().rstrip('!') + '!' :]]",
    data="world",
    tagMap = {
        "{{:": "[[:",
        ":}}": ":]]",
        "{{=": "[[=",   # <-- Not directly used in this example.
        "=}}": "=]]",   # <---^
})
# Output: Hello, World!
```

**2. Percentage Sign For Code Blocks (`%` vs  `@`)**
```py
tplStr = """
%= isLeap = lambda n: (n % 400 == 0) or (n % 100 != 0 and n % 4 == 0)
%= isOrIsNot = "IS" if isLeap(data['year']) else "is NOT"
The year {{: data['year'] :}} {{: isOrIsNot :}} a leap year.
"""
qree.renderStr(tplStr, data={"year": 2020}, tagMap = {
    "@=": "%=",
    "@{": "%{",   # <-- Not directly used in this example.
    "@}": "%}",   # <--^
})
# Output: The year 2020 IS a leap year.
```

**Default `tagMap`:**
The default values for each of the tags is as specified in the dict below.
```py
{   "@=": "@=",
    "@{": "@{",
    "@}": "@}",
    "{{=": "{{=", 
    "=}}": "=}}",
    "{{:": "{{:",
    ":}}": ":}}",
}
```

View Decorator
--------------------
If you're working with [Flask](https://flask.palletsprojects.com/), [Bottle](https://bottlepy.org/) or a similar WSGI framework, `qree.view` can help bind route to templates. 
```py
@app.route("/user-list")
@qree.view("./views/user-list.html", variable="userList")
def serve_userList ():
    userList = yourLogicHere();
    return userList;
```
The above is identical to the following:
```py
@app.route("/user-list")
def serve_user_list_page ():
    userList = yourLogicHere();
    return qree.renderPath("./views/user-list.html",
        data=userList, variable="userList",
    );
```

**Vilo:**  
Using [Vilo](https://github.com/polydojo/vilo) instead of Flask/Bottle? Great choice! Qree jives with Vilo:
```py
@app.route("GET", "/user-list")
@qree.view("./views/user-list.html", variable="userList")
def serve_userList (req, res):
    userList = yourLogicHere(req);
    return userList;
```

**Custom Tags:**  
Like with `qree.renderPath(.)` and `qree.renderStr(.)`, you can use custom tags with `qree.view(.)` by passing `tagMap`.

Testing & Contributing
---------------------------

Install pytest via `pip install -U pytest`. Run tests with:
```
pytest
```

If you encounter a bug, please open an issue on GitHub; but if you find a security vulnerability, please email security@polydojo.com instead.

If you'd like to see a new feature or contribute code, please open a GitHub issue. We'd love to hear from you! Suggestions and code contributions will always be appreciated, big and small.


Licensing
------------
Copyright (c) 2020 Polydojo, Inc.

**Software Licensing:**  
The software is released "AS IS" under the **MIT license**, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. Kindly see [LICENSE.txt](https://github.com/polydojo/qree/blob/master/LICENSE.txt) for more details.

**No Trademark Rights:**  
The above software licensing terms **do not** grant any right in the trademarks, service marks, brand names or logos of Polydojo, Inc.
