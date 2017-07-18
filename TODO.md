# To-do

- [x] Define the file format
- [X] Python library
  - [X] Read file as a stream of records
  - [X] Create and append record
  - [X] Transparently modify record
  - [_] Add `hash` method to Record
- [x] Python implementation
  - [x] Add new bookmark
  - [x] Open Nth bookmark
  - [_] Show Nth bookmark
  - [x] List bookmarks
    - [x] Filter by tag
    - [x] Filter by keywords
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
