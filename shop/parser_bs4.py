from bs4 import BeautifulSoup

text = open("templates/menu.html").read()[20:-15]
soup = BeautifulSoup(text, "html.parser")
out = open("menu.txt", "w")


def t(string):
    """
    add \t
    """
    return (string.count(".")) * "\t" + string


def rec(html):
    id = 0
    s = ""
    l = html.findAll("li")
    for i in l:
        div = i.find("div")
        if div is not None:
            children_id, children_out = rec(i)
            s += f"{t(children_id[:-2])} {div.text}\n"
        else:
            a = i.find("a")
            href = a.get("href")
            if href == "#":
                # print('WARNING ', href, a.text)
                pass
            else:
                id = href[7:]
                s += f"{t(id)} {a.text}\n"
    return id, s


parse = soup.findAll("li", id="parse")

for j in range(len(parse)):
    _, s = rec(parse[j])
    s = f"{j + 1} {parse[j].find('div').text}\n" + s
    out.write(s)
