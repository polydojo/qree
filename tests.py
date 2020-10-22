import qree;

# TODO: Implement proper tests.


print('----------------------------------------------');
print(qree.renderStr("foo\nbar\nbaz"));

print('----------------------------------------------');    
print(qree.renderStr(
    "<h1>Hello {{: data['name'] :}}</h2>",
    {"name": 'World'},
));

print('----------------------------------------------');    
print(qree.renderStr("""
    <ul>
    @= for user in data['userList']:
    @{
        <li>
            <p>Colon para for: {{: user['name'] :}}</p>
            <p>Equal para for: {{= user['name'] =}}</p>
        </li>
    @}
    </ul>
""", {
    "userList": [{"name": "king"}, {"name": "<b>kong</b>"}],
}));

print('----------------------------------------------');
print(qree.renderStr("""
    @= for n in range(1, data):
    @{
        @= if n % 3 == 0 and n % 5 == 0:
        @{
            {{:n:}} Fizz! Buzz!
        @}
        @= elif n % 3 == 0:
        @{
            {{:n:}} Fizz!
        @}
        @= elif n % 5 == 0:
        @{
            {{:n:}} Buzz!
        @}
        @= else:
        @{
            {{:n:}}
        @}
    @}
""", data=16));

print('----------------------------------------------');
print(qree.renderPath("./test-views/homepage.html", {
    "title": "Ich bin die Title!",
    "body": "Und ich bin der Body! ...",
}));
