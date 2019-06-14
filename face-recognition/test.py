import json

def test():
    a = {"name":"go","version":"3.1"}
    print("a",a.get("name"))
    b = json.dumps(a)
    print(b,"|type is",type(b))
    c = json.loads(b)
    print(c,"|type is",type(c))
    pass


test()
