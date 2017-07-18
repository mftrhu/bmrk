# bmrk
A simple plaintext format for bookmarks, and a CLI app.

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
