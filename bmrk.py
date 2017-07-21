#!/usr/bin/env python3
# -*- coding: utf8 -*-
from bookmarks import Bookmarks, Record, StanzaFormatter
import os, re, dateutil.parser, configargparse, webbrowser
import urllib.parse, urllib.request, urllib.error

def external_editor(content=""):
    import tempfile, subprocess
    editor = os.environ.get("EDITOR", "vim")
    with tempfile.NamedTemporaryFile(mode="w+", prefix="bmrk") as file:
        if content:
            file.write(content)
            file.flush()
        exit_code = subprocess.call([editor, file.name])
        if exit_code == 0:
            file.seek(0, 0)
            text = file.read(-1)
            return text.rstrip() + "\n"

def parse(text):
    url, title, tags, desc = None, None, None, ""
    for line in text.splitlines():
        if line.startswith(";"):
            continue
        if url is None:
            url = line.lstrip("<").rstrip(">")
        elif title is None:
            title = line
        elif tags is None and line.startswith(":") and line.endswith(":"):
            tags = line.strip(":").split(":")
        else:
            desc += line + "\n"
    return url, title, tags, desc.rstrip()

def do_add(bookmarks, args):
    url, title = args.url, " ".join(args.title)
    if url is None:
        url = "https://example.com"
        if title is None:
            title = "Title of the bookmark"
    #TODO: Normalize the url
    # If no title, then download the title from the target webpage
    if title is None and not args.no_net:
        try:
            #WARN: will probably raise an error when dealing with pages
            # not in utf-8 - what's the "default" encoding?
            data = urllib.request.urlopen(url).read().decode("utf-8")
            find_title = re.compile("<title>(.*?)</title>", re.IGNORECASE|re.DOTALL)
            title = find_title.search(data).group(1)
        except (urllib.error.URLError, AttributeError):
            pass
    # If no internet, then use the domain itself
    if title is None:
        title = urllib.parse.urlsplit(url).netloc
    tags = args.tags if args.tags is not None else []
    initial_content = (
        "<{0}>\n{1}\n; Tags, separated by :\n:{2}:\n; Add any notes after this line\n"
    ).format(url, title, ":".join(tags))
    # Then open into $EDITOR
    if not args.no_edit:
        url, title, tags, desc = parse(external_editor(initial_content))
    else:
        desc = ""
    # Parse it into a Record and .append() it
    record = Record(url, title, tags=tags, description=desc)
    bookmarks.append(record)

def show(index, bookmark, number=True, title=True, tags=True, url=True,
    description=False):
    out, indent = "", ""
    if number:
        out = "[{0:>4}] ".format(index)
        indent = " " * 7
    if title:
        out += "{0.title}".format(bookmark) + "\n" + indent
    if tags and len(bookmark.tags) > 0:
        out += "#" + " #".join(bookmark.tags) + "\n" + indent
    if url:
        out += "{0.url}".format(bookmark) + "\n" + indent
    if description:
        for line in bookmark.description.splitlines():
            out += line + "\n" + indent
    print(out.strip())

def do_list(bookmarks, args):
    check_tags = lambda b: all(tag in b.tags for tag in args.tags)
    if args.tags is None:
        check_tags = lambda b: True

    check_keywords = lambda b: (any((kw in b.title) for kw in args.keywords)
        or any((kw in b.description) for kw in args.keywords))
    if len(args.keywords) == 0:
        check_keywords = lambda b: True

    for index, bookmark in enumerate(bookmarks):
        if check_keywords(bookmark) and check_tags(bookmark):
            show(index, bookmark)

def ordered_find(bookmarks, ids):
    # Shenanigans to preserve order of ids as given on the command line
    marks = [None] * len(ids)
    checks = [(i, bookmarks._found(id)) for i, id in enumerate(ids)]
    # Following code could likely be much better, but as it stands it
    # should only go through the file once
    for index, bookmark in enumerate(bookmarks):
        for position, found in checks[::]:
            if found(index, bookmark):
                marks[position] = (index, bookmark)
                checks.remove((position, found))
                break
    return list(filter(lambda m: m is not None, marks))

def do_goto(bookmarks, args):
    for index, mark in ordered_find(bookmarks, args.ids):
        webbrowser.open(mark.url)

def do_show(bookmarks, args):
    for index, mark in ordered_find(bookmarks, args.ids):
        if args.url_only:
            print(mark.url)
        else:
            show(index, mark, description=True)

if __name__ == "__main__":
    parser = configargparse.ArgParser(default_config_files=["~/.bmrkrc"],
        ignore_unknown_config_file_keys=True)
    parser.add("-c", "--config", required=False, is_config_file=True,
        help="config file path")
    parser.add("-f", "--file", env_var="BMRK_FILE",
        default="~/bookmarks",
        help="bookmarks file path (default: \"%(default)s\")")
    parser.add("--date-format", env_var="BMRK_DATE_FORMAT",
        default="%Y-%m-%d %H:%M:%S %z",
        help="date format to employ (default: \"%(default)s\")")
    parser.set_defaults(func=lambda *a: parser.print_help())

    subparsers = parser.add_subparsers()

    cmd_add = subparsers.add_parser("add", aliases=["a"],
        help="add a new bookmark")
    cmd_add.add_argument("url", nargs="?", type=str, help="URL to add")
    cmd_add.add_argument("title", nargs="*", help="title of the bookmark")
    cmd_add.add_argument("-t", "--tags", nargs="+", help="optional tags")
    cmd_add.add_argument("-e", "--no-edit", action="store_true",
        help="add the bookmark directly, without editing")
    cmd_add.add_argument("-n", "--no-net", action="store_true",
        help="don't try get the bookmark title from the linked page")
    # -b --batch
    cmd_add.set_defaults(func=do_add)

    cmd_list = subparsers.add_parser("list", aliases=["l", "ls"],
        help="list the bookmarks")
    cmd_list.add_argument("keywords", nargs="*", help="keywords to look for")
    cmd_list.add_argument("-t", "--tags", nargs="+", help="tags to look for")
    # -s --date-start
    # -e --date-end
    # -n --number BMRK_BOOKMARKS_PER_PAGE
    # -p --page
    # -x --export
    # -o --out
    cmd_list.set_defaults(func=do_list)

    cmd_goto = subparsers.add_parser("goto", aliases=["g", "go"],
        help="jump to a bookmark")
    cmd_goto.add_argument("ids", nargs="+", help="id of the bookmark(s) to jump to")
    cmd_goto.set_defaults(func=do_goto)

    cmd_show = subparsers.add_parser("show", aliases=["s", "sh"],
        help="show one or more bookmarks")
    cmd_show.add_argument("ids", nargs="+", help="id of the bookmark(s) to show")
    cmd_show.add_argument("--url-only", action="store_true",
        help="show only the url of the selected bookmarks")
    cmd_show.set_defaults(func=do_show)

    args = parser.parse_args()
    path = os.path.expanduser(args.file)

    formatter = StanzaFormatter(
        date_format=args.date_format,
        date_parser=dateutil.parser.parse
    )
    bookmarks = Bookmarks(path, formatter=formatter)

    args.func(bookmarks, args)
