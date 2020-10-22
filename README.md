

# Qree

Qree (pronounced like 'curry') is a tiny but mighty Python templating engine, geared toward HTML. 'Qree' is short for: *Q*uote, *r*eplace, *e*xec(), *e*val().

Qree is a single python module, under 100 lines of code. Instead of using regular expressions or PEGs, Qree relies on Python's exec() and eval().

It supports all Python language features. Targeted toward Python 3.6+ and Python 2.7+.

## Installation:
You *shall soon* be able to `pip install qree`. But until then, kindly download `qree.py` into your project directory. Then, `import qree` as required.

## Text Interpolation:
Use `{{: expression :}}` for HTML-escaped interpolation, or `{{= expression =}}` for interpolation *without* escaping. The latter is susceptible to XSS, so please be careful with it. Here are a few quick examples:

**1. Hello, World!:**
```py
qree.renderStr("<h2>Hello, {{: data :}}", data="World!")
# Output: <h2>Hello, World!</h2>
```

**2. Using Expressions:**
```py
qree.renderStr("<h2>Mr. {{: data.title() + "!" :}}", data="bond")
# Output: <h2>Mr. Bond!</h2>
```

**3.  HTML Escaping:**
```py
qree.renderStr("<h2>Mr. {{: data :}}", data="<b> Villain </b> ")
# Output: <h2>Mr. &lt;b&gt; Villain &lt;/b&gt; </h2>
```

**4. Without Escaping:**
```py
qree.renderStr("<h2>Mr. {{= data =}}", data="<b> Villain </b> ")
# Output: <h2>Mr. <b> Villain </b> </h2>
```
**5. Longer Example:**
```py
qree.render("""
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
```
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

## Python Code:
Any line beginning with `@=` is treated as Python code. (Preceding whitespace is ignored.)  You can write any python code you wish. You can define variables, import modules, etc. For example:

#### Leap Year Detection Using `lambda`:
```py
tplStr = """
@= isLeap = lambda n: (n % 400 == 0) or (n % 100 != 0 and n % 4 == 0)
@= isOrIsNot = "IS" if isLeap(data['year']) else "is NOT"
The year {{: data['year'] :}} {{: isOrIsNot :}} a leap year.
"""
qree.renderStr(tplStr, data={"year": 2000})
# Output: The year 2000 IS a leap year.

qree.renderStr(tplStr, data{"year": 2001})
# Output: The year 2001 IS NOT a leap year.
```

## Python Indentation:

Python is an indented language. Use the special tags `@{` and `@}` for indicating indentation and de-indentation to Qree, respectively. When used, such a tag should appear by itself on a separate line. For example:

#### Example: Leap Year (with `def`):
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

qree.renderStr(tplStr, data{"year": 2001})
# Output: The year 2001 is NOT a leap year.
```

#### Example: FizzBuzz
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

## The `data` variable:
By default, data passed via the `data` parameter is available in the template as the `data` variable. However, if you'd like to change the variable name, you may do so via the `variable` parameter. For example:
```py
qree.renderStr("Hi {{: name :}}!", data="Jim", variable="name")
# Output: Hi Jim!
```

## Template Files:
It's always convenient to store templates in (or rather, as) separate files. To work with files, use `qree.renderPath(tplPath, data, ...)` instead of `qree.renderStr(tplStr, data, ...)`. 

#### Basic Example:

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

## Nesting Templates:
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

And similarly, footer.html:
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
<doctype html>
<html>
<head><title>{{: data['title'] :}}</title></head>
<body>
{{= qree.renderPath("./views/header.html", data=None) =}}
<h2>{{: data['title'] :}}</h2>
<pre>{{: data['body'] :}}</pre>
{{= qree.renderPath("./views/footer.html", data=None) =}}
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
Now, the output should be:
```html
<doctype html>
<html>
<head><title>The TITLE Goes Here!</title></head>
<body>
<header class="header">
	<a href="/link1">Link 1</a>
	<a href="/link2">Link 2</a>
	<a href="/link3">Link 3</a>
</header>
<h2>The TITLE Goes Here!</h2>
<pre>And the body goes here ...</pre>
<footer class="footer">
	<a href="/linkA">Link A</a>
	<a href="/linkB">Link B</a>
	<a href="/linkC">Link C</a>
</footer>
</body>
<html>
```

In the above example, we passed `data=None` to each nested template. But do realize that we could've passed anything. It's totally up to us. Additionally, as `data=None` is the default, we could've chosen to ignore the `data` parameter.

## License
Qree may be freely distributed under the MIT license. See LICENSE.txt for more details.
