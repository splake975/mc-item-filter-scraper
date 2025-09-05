import bs4

def dump(obj:bs4.Tag):
    # with open("output.html", "w", encoding="utf-8") as f:
    #     f.write(obj.prettify())
    with open("dump.txt", "a", encoding="utf-8") as f:
        pretty_obj = obj.prettify()
        if isinstance(pretty_obj, bytes):
            f.write(pretty_obj.decode("utf-8"))
        if isinstance(pretty_obj, str):
            f.write(pretty_obj)
        # f.write(obj.prettify())
        # or table, or soup, etc.
        f.write("\n")
def test():
    print("hello there")