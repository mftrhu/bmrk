#!/usr/bin/env python3
# -*- coding: utf8 -*-
from bookmarks import Bookmarks, Record, StanzaFormatter
import os, re, sys, stat, dateutil.parser, configargparse, webbrowser
import urllib.parse, urllib.request, urllib.error, datetime

def html_unescape(string):
    try:
        import html
    except ImportError:
        try:
            # Python 2.6-2.7
            from HTMLParser import HTMLParser
        except ImportError:
            # Python 3
            from html.parser import HTMLParser
        html = HTMLParser()
    return html.unescape(string)

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
    taglike = lambda line: line.startswith(":") and line.endswith(":")
    url, title, tags, desc = None, None, None, ""
    for line in text.splitlines():
        if line.startswith(";"):
            continue
        if url is None:
            url = line.lstrip("<").rstrip(">")
        elif title is None:
            title = line
        elif tags is None and taglike(line):
            tags = line.strip(":").split(":")
        else:
            desc += line + "\n"
    return url, title, tags, desc.rstrip()

def do_remove(bookmarks, args):
    mark = bookmarks[args.id]
    if mark is None:
        print("bmrk: no bookmark with id `{0}' exists.".format(args.id))
        return 1
    if not args.yes:
        show(args.id, mark)
        print()
        answer = input("Are you sure you want to delete this bookmark [yes/no]? ")
        if answer.lower() not in ("yes", "y"):
            return 0
    # Delete the bookmark
    del bookmarks[args.id]

def do_edit(bookmarks, args):
    mark = bookmarks[args.id]
    if mark is None:
        print("bmrk: no bookmark with id `{0}' exists.".format(args.id))
        return 1
    initial_content = (
        "<{0}>\n{1}\n; Tags, separated by :\n:{2}:\n"
        "; Add any notes after this line\n"
        "{3}"
    ).format(mark.url, mark.title, ":".join(mark.tags), mark.description)
    # Open into $EDITOR
    content = external_editor(initial_content)
    if content is None:
        print("bmrk: editor quit with an error, canceling.")
        return 3
    url, title, tags, desc = parse(content)
    # "check" for validity
    if len(url) == 0 or len(title) == 0:
        print("bmrk: URL and title cannot be empty.")
        return 2
    record = Record(url, title, created=mark.created, tags=tags,
        description=desc)
    # Finally, save to file
    bookmarks[args.id] = record

def do_add(bookmarks, args):
    url, title = args.url, " ".join(args.title)
    if url is None:
        url = "https://example.com"
        if len(title) == 0:
            title = "Title of the bookmark"
    #TODO: Normalize the url
    # If no title, then download the title from the target webpage
    if len(title) == 0 and not args.no_net:
        try:
            #WARN: will probably raise an error when dealing with pages
            # not in utf-8 - what's the "default" encoding?
            data = urllib.request.urlopen(url).read()
            try:
                data = data.decode("utf-8")
            except UnicodeDecodeError:
                data = data.decode("latin-1")
            find_title = re.compile("<title>(.*?)</title>", re.IGNORECASE|re.DOTALL)
            title = find_title.search(data).group(1)
            title = html_unescape(title)
        except (urllib.error.URLError, AttributeError):
            pass
    # If no internet, then use the domain itself
    if len(title) == 0:
        title = urllib.parse.urlsplit(url).netloc
    title = title.strip()
    tags = args.tags if args.tags is not None else []
    initial_content = (
        "<{0}>\n{1}\n; Tags, separated by :\n:{2}:\n"
        "; Add any notes after this line\n"
    ).format(url, title, ":".join(tags))
    desc = ""
    # Then open into $EDITOR
    if not args.no_edit:
        content = external_editor(initial_content)
        if content is None:
            print("bmrk: editor quit with an error, canceling.")
            return 3
        url, title, tags, desc = parse(content)
    # "check" for validity
    if len(url) == 0 or len(title) == 0:
        print("bmrk: URL and title cannot be empty.")
        return 2
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

def dateify(i):
    return datetime.date(i.year, i.month, i.day)

def day_diff(a, b):
    a, b = dateify(a), dateify(b)
    return (max(a, b) - min(a, b)).days

do_specials = {
    "today": lambda b: day_diff(datetime.date.today(), b.created) < 1,
    "yesterday": lambda b: day_diff(datetime.date.today(), b.created) <= 1,
    "week": lambda b: day_diff(datetime.date.today(), b.created) <= 7,
}

always_true = lambda *a: True

def do_list(bookmarks, args):
    if args.tags is not None:
        include = [tag for tag in args.tags if not tag.startswith("!")]
        exclude = [tag[1:] for tag in args.tags if tag.startswith("!")]
        check_tags = lambda b: (all(tag in b.tags for tag in include) and
            all(tag not in b.tags for tag in exclude))
    else:
        check_tags = lambda b: True

    keywords = [kw.lower() for kw in args.keywords if not kw.startswith(":")]
    specials = [kw.lower()[1:] for kw in args.keywords if kw.startswith(":")]

    check_specials = lambda b: (all(do_specials.get(special, always_true)(b)
        for special in specials))

    check_keywords = lambda b: (any((kw in b.title.lower()) for kw in keywords)
        or any((kw in b.description.lower()) for kw in keywords))
    if len(keywords) == 0:
        check_keywords = lambda b: True

    for index, bookmark in enumerate(bookmarks):
        if (check_specials(bookmark) and check_keywords(bookmark)
            and check_tags(bookmark)):
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

    cmd_edit = subparsers.add_parser("edit", aliases=["e", "ed"],
        help="edit a bookmark")
    cmd_edit.add_argument("id", help="id of the bookmark to edit")
    cmd_edit.set_defaults(func=do_edit)

    cmd_remove = subparsers.add_parser("remove", aliases=["rm"],
        help="edit a bookmark")
    cmd_remove.add_argument("id", help="id of the bookmark to remove")
    cmd_remove.add_argument("-y", "--yes", action="store_true",
        help="do not ask for confirmation on remotion")
    cmd_remove.set_defaults(func=do_remove)

    args = parser.parse_args()
    path = os.path.expanduser(args.file)

    formatter = StanzaFormatter(
        date_format=args.date_format,
        date_parser=dateutil.parser.parse
    )

    bookmarks = Bookmarks(path, formatter=formatter)

    mode = os.fstat(0).st_mode
    # Check whether bmrk is being piped to
    if stat.S_ISFIFO(mode) or stat.S_ISREG(mode):
        tags, no_edit, no_net = args.tags, args.no_edit, args.no_net
        for line in sys.stdin.readlines():
            print("** %s" % line)
    else:
        exit(args.func(bookmarks, args))
