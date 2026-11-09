#!/usr/bin/env python3
"""
character
=========
A person who does not exist.

    python3 character.py check  examples/ada.character
    python3 character.py report examples/ada.character

There is no ground truth here to check against, so this asks a different
question from `remember`: not "did you see this" but "if she acts against her
own nature, is the reason on the page?"

Checked against: internal consistency.
"""

import sys

import core
from core import PortraitError

COMMANDS = ("check", "report")

USAGE = """character

  python3 character.py check  path/to/file
  python3 character.py report path/to/file

A person you are inventing. Every scene either shows a trait or breaks one,
and a break needs a reason.
"""


# ---------------------------------------------------------------------------
# The model
# ---------------------------------------------------------------------------

class Trait:
    def __init__(self, name, line):
        self.name = name
        self.line = line
        self.when = None


class Scene:
    def __init__(self, name, line):
        self.name = name
        self.line = line
        self.does = None
        self.shows = []
        self.against = []
        self.because = None


class Portrait:
    def __init__(self, name, line):
        self.mode = "character"
        self.name = name
        self.line = line
        self.props = {}
        self.traits = []
        self.scenes = []


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def parse(source):
    mode, name, body = core.header(source)
    if mode != "character":
        raise PortraitError(
            "this is a %s portrait, not a character" % mode, 1,
            hint="character.py only reads portraits that begin with "
                 "'character'",
        )
    core.require_end(body)

    doc = Portrait(name, 1)
    current = None

    for number, text in body:
        word = text.split(None, 1)[0]
        rest = text[len(word):].strip()

        if text == "end":
            break

        if word == "trait":
            if not rest:
                raise PortraitError("a trait needs a name", number)
            current = Trait(rest, number)
            doc.traits.append(current)
            continue

        if word == "scene":
            if not rest:
                raise PortraitError("a scene needs a name", number)
            current = Scene(rest, number)
            doc.scenes.append(current)
            continue

        if word == "when" and isinstance(current, Trait):
            current.when = rest
        elif word == "does" and isinstance(current, Scene):
            current.does = rest
        elif word == "shows" and isinstance(current, Scene):
            current.shows.append(rest)
        elif word == "against" and isinstance(current, Scene):
            current.against.append(rest)
        elif word == "because" and isinstance(current, Scene):
            current.because = rest
        elif word == "role":
            doc.props["role"] = rest
        else:
            raise PortraitError(
                "I do not know what '%s' means here" % word, number,
                hint="a character has trait and scene; a scene has does, "
                     "shows, against and because",
            )

    return doc


# ---------------------------------------------------------------------------
# Checking
# ---------------------------------------------------------------------------

def check(doc):
    warnings = []
    names = {t.name for t in doc.traits}

    if not doc.traits:
        raise PortraitError(
            "%s has no traits, so nothing can be consistent" % doc.name,
            doc.line,
        )

    for trait in doc.traits:
        if trait.when is None:
            raise PortraitError(
                "'%s' has no room" % trait.name, trait.line,
                hint="a character is not one thing everywhere either. Say "
                     "when this holds:\n        when  when someone is "
                     "watching",
            )

    for scene in doc.scenes:
        for name in scene.shows + scene.against:
            if name not in names:
                raise PortraitError(
                    "this scene mentions '%s', which is not a trait of %s"
                    % (name, doc.name), scene.line,
                    hint="the traits are: "
                         + (", ".join(sorted(names)) if names else "none yet"),
                )
        if scene.against and scene.because is None:
            raise PortraitError(
                "this scene breaks '%s' with no reason given"
                % scene.against[0], scene.line,
                hint="a character who breaks their own nature needs a "
                     "reason on the page:\n        because  she is "
                     "dissociating",
            )
        if not scene.shows and not scene.against:
            warnings.append(
                "line %d: scene '%s' does nothing to %s"
                % (scene.line, scene.name, doc.name)
            )

    shown = set()
    for scene in doc.scenes:
        shown.update(scene.shows)
    for trait in doc.traits:
        if trait.name not in shown:
            warnings.append(
                "line %d: '%s' is established but never shown in a scene"
                % (trait.line, trait.name)
            )
    return warnings


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def report(doc):
    out = ["%s — character" % doc.name, ""]
    out.append("  traits   %d" % len(doc.traits))
    for trait in doc.traits:
        out.append("    %-22s when %s" % (trait.name, trait.when))
    out.append("")
    out.append("  scenes   %d" % len(doc.scenes))

    breaks = 0
    for scene in doc.scenes:
        marks = ["shows %s" % n for n in scene.shows]
        for name in scene.against:
            marks.append("breaks %s" % name)
            breaks += 1
        out.append("    %-22s %s" % (scene.name, ", ".join(marks) or "—"))
        if scene.does:
            out.append("      does     %s" % scene.does)
        if scene.because:
            out.append("      because  %s" % scene.because)
    out.append("")
    out.append("  %d deliberate break%s."
               % (breaks, "" if breaks == 1 else "s"))
    return "\n".join(out).rstrip()


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def handle(command, path, source):
    doc = parse(source)
    warnings = check(doc)

    for warning in warnings:
        sys.stderr.write("%s: warning: %s\n" % (path, warning))

    if command == "check":
        note = ", with the notes above" if warnings else ""
        print("%s: reads clearly (a character portrait)%s" % (path, note))
    else:
        print(report(doc))
    return 0


def main(argv):
    return core.run(argv, COMMANDS, handle, USAGE)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
