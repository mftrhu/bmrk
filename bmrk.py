#!/usr/bin/env python3
# -*- coding: utf8 -*-
from bookmarks import Bookmarks, Record, StanzaFormatter
import os, dateutil.parser, configargparse

def do_add(bookmarks, args):
    # Normalize the url
    # If no title, then download the title from the target webpage
    # If no internet, then use the domain itself
    # Then open into $EDITOR
    # Parse it into a Record and .append() it
    record = Record(args.url, args.title, tags=args.tags)
    print(record)

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
            print("[{0:>4}] {1.title}".format(index, bookmark))
            if len(bookmark.tags) > 0:
                print("       #{0}".format(" #".join(bookmark.tags)))
            print("       <{0}>".format(bookmark.url))

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
    cmd_add.add_argument("url", type=str, help="URL to add")
    cmd_add.add_argument("tags", nargs="*", help="optional tags")
    cmd_add.add_argument("-t", "--title", help="title of the bookmark")
    cmd_add.add_argument("-n", "--no-edit", action="store_true",
        help="add the bookmark directly, without editing")
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

    args = parser.parse_args()
    path = os.path.expanduser(args.file)
    
    formatter = StanzaFormatter(
        date_format=args.date_format,
        date_parser=dateutil.parser.parse
    )
    bookmarks = Bookmarks(path, formatter=formatter)

    args.func(bookmarks, args)
