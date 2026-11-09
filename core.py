#!/usr/bin/env python3
"""
The little that every portrait shares.

This is deliberately small.  The four kinds of portrait do not share a data
model, a reader, or a checker.  They share:

  * an error format
  * a way of turning a file into numbered, comment-free lines
  * one convention about what a date looks like
  * the rule that a portrait ends with 'end'

That is all.  Everything else is per-kind, which is why each kind lives in
its own file and can be run on its own.
"""

import re
import sys

MODES = ("remember", "understand", "character", "simulate")

DATE = re.compile(r"\A\d{4}-\d{2}(-\d{2})?\Z")


class PortraitError(Exception):
    """An error with a line number and, where possible, the fix."""

    def __init__(self, message, line=None, hint=None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.hint = hint


def render_error(err, source, filename):
    lines = source.split("\n")
    out = ["%s: error: %s" % (filename, err.message)]
    if err.line is not None:
        out.append("")
        out.append("  at line %d" % err.line)
        if 1 <= err.line <= len(lines):
            out.append("      " + lines[err.line - 1].rstrip())
    if err.hint:
        out.append("")
        out.append("  " + err.hint)
    return "\n".join(out)


def tidy(source):
    """Numbered, comment-free, non-blank lines."""
    out = []
    for number, raw in enumerate(source.split("\n"), 1):
        body = raw.split("#", 1)[0].rstrip()
        if body.strip():
            out.append((number, body.strip()))
    return out


def article(word):
    """'a' or 'an', so the error messages read like English."""
    return "an" if word[:1] in "aeiou" else "a"


def unquote_items(text):
    return [p.strip().strip('"').strip("'")
            for p in text.split(",") if p.strip()]


def header(source):
    """Split a portrait into (kind, name, remaining lines)."""
    lines = tidy(source)
    if not lines:
        raise PortraitError("this file is empty", 1)

    number, text = lines[0]
    parts = text.split(None, 1)
    if parts[0] not in MODES:
        raise PortraitError(
            "'%s' is not a kind of portrait" % parts[0], number,
            hint="a portrait begins with one of: " + ", ".join(MODES),
        )
    if len(parts) < 2:
        raise PortraitError(
            "this portrait has no name", number,
            hint="write: %s Ada" % parts[0],
        )
    return parts[0], parts[1].strip(), lines[1:]


def require_end(body):
    if not any(text == "end" for _number, text in body):
        raise PortraitError(
            "this portrait is never closed", body[-1][0] if body else 1,
            hint="the last line should be 'end'",
        )


def run(argv, commands, handle, usage):
    """The command line every portrait program shares.

    `handle(command, path, source)` returns an exit code or raises
    PortraitError.
    """
    if len(argv) < 3 or argv[1] not in commands:
        sys.stderr.write(usage)
        return 2

    command, path = argv[1], argv[2]
    try:
        with open(path, "r") as opened:
            source = opened.read()
    except FileNotFoundError:
        sys.stderr.write("there is no file called %s\n" % path)
        return 2

    try:
        return handle(command, path, source)
    except PortraitError as err:
        sys.stderr.write(render_error(err, source, path) + "\n")
        return 1
