# To-do

- [x] Define the file format
- [x] Python library
  - [x] Read file as a stream of records
  - [x] Create and append record
  - [x] Transparently modify record
  - [_] Add `hash` method to Record
  - [x] Disable word-wrap/shunt it to the frontend
- [x] Python implementation
  - [x] Add new bookmark
  - [x] Open Nth bookmark
  - [_] Show Nth bookmark
    - [_] URL-only
  - [x] List bookmarks
    - [x] Filter by tag
    - [x] Filter by keywords
    - [_] Filter by site (e.g. `site:*.wikipedia.org`)
  - [_] Edit Nth bookmark
  - [_] Delete Nth bookmark

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
