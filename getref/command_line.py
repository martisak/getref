import argparse
import requests
import json
from simple_term_menu import TerminalMenu
from pygments import highlight
from pygments.lexers.bibtex import BibTeXLexer
from pygments.formatters import TerminalFormatter

def args_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'query',metavar="QUERY", help='Search query', action="append")

    return parser.parse_args()

def query(query):
    r = requests.get('http://dblp.uni-trier.de/search/publ/api', params={'q': query, 'h':100, 'format': 'json'})
    json_answer = r.json()

    hits = {}

    results = json_answer["result"]["hits"].get("hit", None)
    if results is None:
        return None

    for n, hit  in enumerate(results):
        if hit is None: continue
        authors = hit["info"].pop("authors")
        hit["info"]["authors"] = [a["text"] for a in authors["author"]]
        hit["info"]["bibtex"] = get_bib(hit["info"]["key"])
        hits.update({n: hit["info"]})

    return hits

def menu(hits):

    items = []
    for k, v in hits.items():

        if len(v["authors"]) > 3:
            authors = ", ".join(v["authors"][0:3]) + ", et al."
        else:
            authors = ", ".join(v["authors"])

        items.append("{}, {}, {}|{}".format(authors, v["title"], v["venue"],k))

    def return_bib(k):
        code = hits[int(k)].get("bibtex", "")
        formatter = TerminalFormatter(bg="dark")
        return highlight(code, BibTeXLexer(), formatter)

    terminal_menu = TerminalMenu(items, preview_command=return_bib, preview_size=0.75)
    menu_entry_index = terminal_menu.show()
    return menu_entry_index


def get_bib(key):
    r = requests.get('http://dblp.uni-trier.de/rec/bib2/{}.bib'.format(key))
    return r.text.strip()

def main():
    args = args_parser()

    hits = query(args.query)

    if hits is None:
        quit()

    item = menu(hits)
    print(get_bib(hits[item]["key"]))

if __name__ == "__main__":
    main()
