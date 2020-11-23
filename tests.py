import qree;
import pytest;

# Run tests with:
#       pytest tests.py -vv

def test_identity ():
    assert qree.renderStr("plain") == "plain";
    assert qree.renderStr('foo\nbar\nbaz') == 'foo\nbar\nbaz';

def test_basic_substitution ():
    tpl = "Hello, {{: data + '!' :}}";
    assert qree.renderStr(tpl, "World") == 'Hello, World!';
    assert qree.renderStr(tpl, "> World") == 'Hello, &gt; World!';
    tpl2 = "Hello, {{= data + '!' =}}";
    assert qree.renderStr(tpl2, "World") == 'Hello, World!';
    assert qree.renderStr(tpl2, "> World") == 'Hello, > World!';

def test_nonPyQuotesOk ():
    "Test that single-quotes _outside_ py-code are OK.";
    qree.renderStr("Trip ''' quotes") == "Trip ''' quotes";
    qree.renderStr("'{{: data :}}'", None) == "'None'";

def test_pyQuotesOk ():
    "Test that single-quotes _within_ py-code are OK.";
    qree.renderStr("{{: data['foo'] :}}", {"foo": "bar"}) == "bar";
    qree.renderStr("{{: data['''foo'''] :}}", {"foo": "bar"}) == "bar";

def test_substitution_tag_error ():
    badTplList =[
        "Hello, {{: data + '!' ]]",             # Unclosed
        "Hello, {{= {{: data + '!' :}} =}}",    # Nesting banned
        "Hello, {{: {{= data + '!' =}} :}}",
        """
        @= import qree;
        {{: qree.renderStr('{{= data.title() =}}', data=data) :}}
        """,
    ];
    for badTpl in badTplList:
        with pytest.raises(SyntaxError):
            qree.renderStr(badTpl, "World");

def test_indent_tag_error ():
    badTplList = [
        # 1, 2 :
        "@{", "@}",
        # --------------------------
        # 3:
        """
        @= if True:
        @{
            Unclosed indent.
        #
        """,
        # --------------------------
        # 4:
        """
        @= if True:
        #
            Unopened indent.
        @}
        """,
        # --------------------------
        # 5:
        """
        @= if True:
        @{
            if True:
            @{
                Unclosed inner indent.
            #
        @}
        """,
        # --------------------------
        # 6:
        """
        @= if True:
        @{ Non-comment line along w/ open-indent.
        @}
        """,
        # --------------------------
        # 7:
        """
        @= if True:
        @{
        @} Non-comment line along w/ close-indent.
        """,
    ];
    assert len(badTplList) == 7;
    for badTpl in badTplList:
        with pytest.raises(IndentationError):
            print(qree.renderStr(badTpl, data=None));

def test_basic_indent ():
    tpl = """
    @= for n in range(1, data+1):
    @{
        {{: n :}} is {{: 'EVEN' if n % 2 == 0 else 'ODD' :}}
    @}
    """;
    expected = """
        1 is ODD
        2 is EVEN
        3 is ODD
        4 is EVEN
    """;
    assert qree.renderStr(tpl, data=4) == expected;

def test_nested_indent ():
    tpl = """
    @= for n in range(1, data+1):
    @{
        @= if n % 15 == 0:
        @{  # Comment w/ indent-open.
            FizzBuzz!
        @}
        @= elif n % 3 == 0:
        @{
            Fizz!
        @}  # Comment w/ indent-close.
        @= elif n % 5 == 0:
        @{
            Buzz!
        @}
        @= else:
        @{
            {{: n :}}
        @}
    @}
    """;
    expected = """
            1
            2
            Fizz!
            4
            Buzz!
            Fizz!
            7
            8
            Fizz!
            Buzz!
            11
            Fizz!
            13
            14
            FizzBuzz!
    """;
    assert qree.renderStr(tpl, data=15) == expected;
    

def test_renderPath_basic_plus_with_view ():
    footerPath = "./test-views/footer.html";
    expectedFooter = "\n".join([
        '<footer class="footer">',
        '    <a href="/linkA">Link A</a>',
        '    <a href="/linkB">Link B</a>',
        '    <a href="/linkC">Link C</a>',
        '</footer>',
        '', # <-- Qree seems to like adding trailing newlines.
    ]);
    print(repr(expectedFooter));
    print(repr(qree.renderPath(footerPath)));
    assert qree.renderPath(footerPath) == expectedFooter;
    
    @qree.view(footerPath)
    def serveFooter ():
        return None;
    assert serveFooter() == expectedFooter;


def test_renderPath_nested_plus_with_view ():
    homepagePath = "./test-views/homepage.html";
    data = {
        "title": "... TITLE 2 ...",
        "body": "... BODY 2 ...",
    }
    expectedHomepage = "\n".join([
        '<doctype html>',
        '<html>',
        '<head><title>... TITLE 2 ...</title></head>',
        '<body>',
        '<header class="header">',
        '    <a href="/link1">Link 1</a>',
        '    <a href="/link2">Link 2</a>',
        '    <a href="/link3">Link 3</a>',
        '</header>',
        '',                             # <-- \n via nested call.
        '<h2>... TITLE 2 ...</h2>',
        '<pre>... BODY 2 ...</pre>',
        '<footer class="footer">',
        '    <a href="/linkA">Link A</a>',
        '    <a href="/linkB">Link B</a>',
        '    <a href="/linkC">Link C</a>',
        '</footer>',
        '',                             # <-- \n via nested call.
        '</body>',
        '<html>',
        '', # <-- Qree seems to like adding trailing newlines.
    ]);
    assert qree.renderPath(homepagePath, data) == expectedHomepage;
    
    @qree.view(homepagePath)
    def serveHomepage ():
        return data;
    assert serveHomepage() == expectedHomepage;
    
    print(expectedHomepage);
test_renderPath_nested_plus_with_view();

# End ######################################################
