import argparse
import requests
import json
import sys
from simple_term_menu import TerminalMenu
from pygments import highlight
from pygments.lexers.bibtex import BibTeXLexer
from pygments.formatters import TerminalFormatter
from multiprocess import Process, Manager
import shutil


def fullname(str1):
    # split the string into a list
    lst = str1.split()
    newspace = ""

    for l in lst[:-1]:
        newspace += (l[0].upper() + '. ')

    newspace += lst[-1].title()
    return newspace


def args_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'query', metavar="QUERY", nargs='+', help='Search query')
    parser.add_argument('--all', action='store_true', help='print all hits')

    return parser.parse_args()


def query(query_lst):

    manager = Manager()
    hits = manager.dict()

    results = []

    for q in query_lst:
        r = requests.get('http://dblp.uni-trier.de/search/publ/api',
                         params={'q': q, 'h': 100, 'format': 'json'})

        if r.status_code == 429:
            raise Error

        json_answer = r.json()

        res = json_answer["result"]["hits"].get("hit", None)

        if res is None:
            continue

        results += res

    def f(d, hit, n):

        if hit is None:
            return

        authors = hit["info"].pop("authors")
        if isinstance(authors["author"], dict):
            hit["info"]["authors"] = authors["author"]["text"]
        else:
            hit["info"]["authors"] = [
                fullname(a["text"]) for a in authors["author"]]

        hit["info"]["bibtex"] = get_bib(hit["info"]["key"])
        d[n] = hit["info"]

    job = [Process(target=f, args=(hits, hit, n))
           for n, hit in enumerate(results)]
    _ = [p.start() for p in job]
    _ = [p.join() for p in job]

    return dict(hits)


def shorten_authors(authlist):
    if len(authlist) > 3:
        return ", ".join(authlist[0:3]) + ", et al."

    return ", ".join(authlist)

def menu(hits):
    width = shutil.get_terminal_size((80, 20))[0]

    max_author_width = max([len(shorten_authors(v["authors"])) for k, v in hits.items()])

    offset = 2
    third_col = 30
    first_col = max_author_width + 1
    second_col = width - third_col - first_col - offset

    items = []

    for k, v in hits.items():

        authors = shorten_authors(v["authors"])
        items.append("{author:<{first_col}}{title:<{second_col}}{venue:>{third_col}}|{k}".format(
            author=authors.strip(), title=v["title"].strip(),
            venue=v["venue"].strip(), k=k, first_col=first_col,
            second_col=second_col,third_col=third_col))

    def return_bib(k):
        code = hits[int(k)].get("bibtex", "")
        formatter = TerminalFormatter(bg="dark")
        return highlight(code, BibTeXLexer(), formatter)

    terminal_menu = TerminalMenu(
        items, preview_command=return_bib, preview_size=0.75)
    menu_entry_index = terminal_menu.show()
    return menu_entry_index


def get_bib(key):
    r = requests.get(f"http://dblp.uni-trier.de/rec/bib2/{key}.bib")
    return r.text.strip()


def main():
    args = args_parser()

    input_raw = query(args.query)

    hits = {}
    for key,value in input_raw.items():
        if value not in hits.values():
            hits[key] = value

    if hits is None:
        sys.exit()

    if args.all:
        for k,v in hits.items():
            print(v["bibtex"])

    else:
        item = menu(hits)
        if item is not None:
            print(hits[item]["bibtex"])


if __name__ == "__main__":
    main()
