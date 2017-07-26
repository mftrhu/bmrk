# To-do

- [x] Define the file format
- [x] Python library
  - [x] Read file as a stream of records
  - [x] Create and append record
  - [x] Transparently modify record
  - [ ] Add `hash` method to Record
  - [x] Disable word-wrap/shunt it to the frontend
  - [ ] Make `__getitem__`, `__setitem__` & co behave properly (AKA,
        raise exceptions)
- [x] Python implementation
  - [x] Add new bookmark
    - [x] Get title from linked page
    - [ ] Get tags from linked page (<meta>?)
  - [x] Open Nth bookmark
  - [x] Show Nth bookmark
    - [x] URL-only
  - [x] List bookmarks
    - [x] Filter by tag
    - [x] Filter by keywords
    - [x] Filter by `:today`, `:yesterday`, ...
    - [ ] Filter by site (e.g. `site:*.wikipedia.org`)
  - [x] Edit Nth bookmark
    - [ ] Edit multiple bookmarks?
  - [x] Delete Nth bookmark
    - [x] "Are you sure you want to delete [...]?", plus `--yes`
    - [ ] Delete multiple bookmarks?
  - [x] Write documentation

## Possible features

- [ ] Add bookmarks by piping URLs
- [ ] Multiple format readers/writers
  - [ ] Single-line, tab-delimited
  - [ ] Netscape HTML
  - [ ] JSONL
  - [ ] Buku
  - [ ] Other bookmarking services
- [ ] Uniquely identify bookmark by hash
- [ ] Use short hash (say, first ~3-4 Base32 letters) to jump to them
- [ ] Associate aliases to bookmarks
