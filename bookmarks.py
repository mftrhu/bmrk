#!/usr/bin/env python3
# -*- coding: utf8 -*-
import datetime, tempfile

# Following shenanigans thanks to this vbem's StackOverflow [answer]
# [answer]: <https://stackoverflow.com/a/39079819/8070745>
local_tz = lambda: datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

def overwrite(source, dest):
    source_opened, dest_opened = False, False
    if type(source) is str:
        source, source_opened = open(source, "r"), True
    if type(dest) is str:
        dest, dest_opened = open(dest, "w"), True
    source.seek(0)
    for line in source:
        dest.write(line)
    if source_opened: source.close()
    if dest_opened: dest.close()

class Record(object):
    def __init__(self, url, title, created=None, tags=None, description=None):
        self.url, self.title = url, title
        if created is None:
            created = datetime.datetime.now(local_tz())
        self.created = created
        if tags is None:
            tags = []
        self.tags = list(filter(lambda i: len(i) > 0, tags))
        self.description = description

    def __repr__(self):
        return "{} <{}>".format(self.title, self.url)

class StanzaFormatter(object):
    def __init__(self, date_format=None, separator="---", comment=";",
    date_parser=None):
        if date_format is None:
            date_format = "%Y-%m-%d %H:%M:%S %z"
        self.date_format = date_format
        if date_parser is None:
            date_parser = lambda string: datetime.datetime.strptime(string,
                self.date_format)
        self.date_parser = date_parser
        self.separator = separator
        self.comment = comment

    def escape(self, line):
        if (line.startswith(self.comment)
            or line.startswith(self.separator)
            or line.startswith("\\")):
            line = "\\" + line
        return line

    def unescape(self, line):
        if line.startswith("\\"):
            return line[1:]
        return line

    def write(self, record):
        if type(record) is str:
            return record
        out = "{}\n<{}>\n{}\n".format(
            record.created.strftime(self.date_format), record.url,
            self.escape(record.title))
        if len(record.tags) > 0:
            out += ":{}:\n".format(":".join(record.tags))
        if record.description:
            for line in record.description.splitlines():
                out += self.escape(line).rstrip()
                out += "\n"
        out += self.separator + "\n"
        return out

    def read(self, file):
        date, url, title, tags, desc = None, None, None, None, ""
        valid = lambda: (date is not None and url is not None
            and title is not None)
        if type(file) is str:
            file = open(file, "r")
        for line in file:
            line = line.rstrip()
            if line.startswith(self.comment):
                yield line + "\n"
            elif date is None:
                try:
                    date = self.date_parser(line)
                except ValueError as e:
                    date = None
            elif url is None:
                url = line.lstrip("<").rstrip(">")
            elif title is None:
                title = self.unescape(line)
            elif tags is None and line.startswith(":"):
                tags = line.strip(":").split(":")
            elif line != self.separator:
                desc += self.unescape(line) + "\n"
            elif valid:
                yield Record(url, title, date, tags, desc)
                date, url, title, tags, desc = None, None, None, None, ""
            else:
                continue
        file.close()

class Bookmarks(object):
    def __init__(self, path, formatter=StanzaFormatter(),
    preserve_comments=True):
        self.path = path
        self.formatter = formatter
        self.preserve_comments = preserve_comments

    def _found(self, key):
        """
          For internal use only.

          Given a key, which can be an integer or a string, returns a
          function to identify the proper record.
        """
        if type(key) is slice:
            return lambda index, record: key.start <= index < key.stop
        try:
            key = int(key)
            return lambda index, record: index == key
        except ValueError:
            return lambda index, record: record.hash().startswith(key)

    def __iter__(self):
        """
          Iterates through the bookmarks file, yielding records.
        """
        for record in self.formatter.read(self.path):
            if type(record) is Record:
                yield record

    def __len__(self):
        """
          Iterates through the bookmarks file and returns the number of
          valid records.
        """
        count = 0
        for record in self:
            count += 1
        return count

    def _getslice(self, found):
        """
          For internal use only.

          Yields a generator containing all the records that satisfy the
          condition specified by `found`.
        """
        index = 0
        for record in self.formatter.read(self.path):
            if type(record) is not Record:
                continue
            if found(index, record):
                yield record
            index += 1

    def __getitem__(self, key):
        """
          Iterates through the files and returns the record with key
          `key`, either an integer (by index) or a string (by hash).
        """
        found = self._found(key)
        if type(key) is slice:
            return self._getslice(found)

        index = 0
        for record in self.formatter.read(self.path):
            if type(record) is not Record:
                continue
            if found(index, record):
                return record
            index += 1

    def __setitem__(self, key, value):
        """
          Replaces the item at position `key`, by copying all the
          records to a temporary file, writing the new record, the rest,
          and then overwriting the existing file with the new contents.

          **Warning:** it will remove spurious content, unless within a
            comment with `preserve_comments` set to `True`.
        """
        found = self._found(key)
        with tempfile.TemporaryFile("r+") as file:
            index = 0
            for record in self.formatter.read(self.path):
                if self.preserve_comments and type(record) is not Record:
                    file.write(record)
                    continue
                if found(index, record):
                    file.write(self.formatter.write(value))
                else:
                    file.write(self.formatter.write(record))
                index += 1

            overwrite(source=file, dest=self.path)

    def __delitem__(self, key):
        """
          Deletes an item by copying all the records 'till key, and
          after key, to a new file that will then replace the original.

          **Warning:** as per `__setitem__`, this function will remove
            spurious content, not commented (and even then only when
            `preserve_comments` has been set to `True`).
        """
        found = self._found(key)
        with tempfile.TemporaryFile("r+") as file:
            index = 0
            for record in self.formatter.read(self.path):
                if type(record) is Record and found(index, record):
                    pass
                else:
                    file.write(self.formatter.write(record))
                index += int(type(record) is Record)

            overwrite(source=file, dest=self.path)

    def append(self, record):
        """
          Appends a new record to the bookmarks file.
        """
        with open(self.path, "a") as file:
            file.write(self.formatter.write(record))
