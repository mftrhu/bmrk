# bmrk
A simple plaintext format for bookmarks, and a CLI app.

## Usage

The CLI app *tries* (success is not guaranteed) to be simple to use. It
offers six sub-commands: add, list, goto, show, edit and remove.

### add

**Params:** `[URL] [TITLE...] [-t|--tags TAGS...] [-e|--no-edit] [-n|--no-net]`  
**Aliases:** `a`

Adds a bookmark to the bookmarks file, with URL `URL`, title `TITLE` and
tags `TAGS`. If any of these (or even all of them) are absent, `bmrk`
either leaves the relevant field empty (for tags) or tries to fill it
with something useful - for example, getting the title of the page from
the page itself (unless `--no-net` was selected).

Unless `--no-edit` was specified `bmrk` will then open the default editor
(as specified by the environment variable `EDITOR`), allowing the user to
modify the data and optionally add a description.

### list

**Params:** `[KEYWORDS...] [-t|--tags TAGS...]`  
**Aliases:** `l`, `ls`

Shows a list of the bookmarks that conform to the query - that is, that
contain `KEYWORDS` in their title or description, and that contain all
the `TAGS` specified. 

If no keywords/tags are specified then shows all the bookmarks.

Example output:

    $ bmrk
    [   0] Example website
           #example #website #whew #redundancy
           https://example.com

Keywords starting with `:` are treated differently. As of this time, only 
`:today`, `:yesterday` and `:week` exist - they are used as shorthands to
specify a time range that extends to the current day. AKA, `:today` will
show only the bookmarks added within the last 24 hours, `:yesterday`
those added within the last two days and so on.

### goto

**Params:** `ID...`  
**Aliases:** `g`, `go`

Opens the bookmark(s) specified by `ID` in the default web browser.

### show

**Params:** `ID... [--url-only]`  
**Aliases:** `s`, `sh`

Shows the bookmark(s) specified by `ID`, including the description -
unless `--url-only` was specified, which results in a list of the URLs.

### edit

**Params:** `ID`  
**Aliases:** `e`, `ed`

Opens the bookmark specified by `ID` in the default editor and updates it
accordingly. 

### remove

**Params:** `ID [-y|--yes]`  
**Aliases:** `rm`

Deletes the bookmark specified by `ID`, showing the bookmark and asking
for confirmation unless `--yes` was specified.

## Format definition

The format of the file itself should be simple, with an implicit and
human-readable structure.

    Creation date (Format: %Y-%m-%d %H:%M:%S %Z)
    <URL of the resource, normalized>
    Title of the bookmark
    [:tag:tag:tag:tag:]
    [Multi-line description of the resource]
    ---

The file will be organized in stanzas, each separated from the other by
a sequence of three dashes (`---`) on a line by itself.

A line starting with `#` should be ignored as a comment. Comments may be
preserved by the implementation.

If this sequence should appear in either the title or the description, it
should be escaped by prepending a `\` to it. `\`, and `#`, should be 
escaped in the same way.

To be valid, a record must have a creation date, an URL and a title. The
title may be empty, in which case it may be filled by the program with
the title of the web-page the URI points to, or with its domain.

The URL should not be empty (`<>`); records with an empty URL should be
considered as invalid.

Invalid records should be ignored.
