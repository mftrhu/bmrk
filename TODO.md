# To-do

- [x] Define the file format
- [_] Python library
  - [_] Read file as a stream of records
  - [_] Create and append record
  - [_] Transparently modify record
- [_] Python implementation
  - [_] Add new bookmark
  - [_] Open/show Nth bookmark
  - [_] List bookmarks
    - [_] Filter by tag
    - [_] Filter by keywords
    - [_] Filter by site (e.g. `site:*.wikipedia.org`)
  - [_] Edit Nth bookmark

## Possible features

- [_] Add bookmarks by piping URLs
- [_] Multiple format readers/writers
  - [_] Single-line, tab-delimited
  - [_] Netscape HTML
  - [_] JSONL
  - [_] Buku
  - [_] Other bookmarking services
- [_] Uniquely identify bookmark by hash
- [_] Use short hash (say, first ~3-4 Base32 letters) to jump to them
- [_] Associate aliases to bookmarks
