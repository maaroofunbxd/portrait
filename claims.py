#!/usr/bin/env python3
"""
The claim machinery that remember and understand share.

Not a tool.  Nothing here is ever run directly.  This is the model — a claim
with a room, a basis and a date — the reader for that model, and the laws
both kinds enforce:

  * a trait with no room is a trait that will mislead you
  * a trait with no basis is a conclusion, not a memory
  * an undated trait cannot be checked later
  * a person is one thing with many names, never several copies

`understand` adds one more rule on top of these, and that rule lives in
understand.py, because it is understand's rule and not remember's.
"""

import core

WEAK_WORDS = ("once", "one time", "twice", "two times", "a couple")
CLAIM_FIELDS = ("when", "because", "on", "revised")


# ---------------------------------------------------------------------------
# The model
# ---------------------------------------------------------------------------

class Claim:
    """One thing you think you know, with its room, its basis and its date."""

    def __init__(self, kind, trait, line):
        self.kind = kind          # observed | inferred
        self.trait = trait
        self.line = line
        self.when = None
        self.because = None
        self.on = None
        self.revisions = []       # list of (date, note)


class Contrast:
    """An acknowledgement that a trait holds differently in two rooms."""

    def __init__(self, trait, line):
        self.trait = trait
        self.line = line
        self.because = None


class Portrait:
    def __init__(self, mode, name, line):
        self.mode = mode
        self.name = name
        self.line = line
        self.props = {}
        self.claims = []
        self.contrasts = []

    def claims_for(self, trait):
        return [c for c in self.claims if c.trait == trait]


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def parse(source, expected):
    """Read a portrait that must begin with `expected`."""
    mode, name, body = core.header(source)
    if mode != expected:
        raise core.PortraitError(
            "this is %s %s portrait, not %s %s one"
            % (core.article(mode), mode, core.article(expected), expected), 1,
            hint="%s.py only reads portraits that begin with '%s'"
                 % (expected, expected),
        )
    core.require_end(body)

    doc = Portrait(mode, name, 1)
    current = None

    for number, text in body:
        word = text.split(None, 1)[0]
        rest = text[len(word):].strip()

        if text == "end":
            break

        if word in ("observed", "inferred"):
            if not rest:
                raise core.PortraitError(
                    "a '%s' needs to say what it is about" % word, number,
                    hint="write: %s patient" % word,
                )
            current = Claim(word, rest, number)
            doc.claims.append(current)
            continue

        if word == "contrast":
            if expected != "understand":
                raise core.PortraitError(
                    "'contrast' belongs to an understand portrait", number,
                    hint="remember keeps a record; understand is where two "
                         "rooms are joined. Put this in an understand file.",
                )
            if not rest:
                raise core.PortraitError("'contrast' needs a trait", number)
            current = Contrast(rest, number)
            doc.contrasts.append(current)
            continue

        if word in CLAIM_FIELDS and current is not None:
            set_field(current, word, rest, number)
            continue

        if word == "role":
            doc.props["role"] = rest
        elif word == "met":
            doc.props["met"] = rest
        elif word == "currently":
            doc.props["currently"] = rest
        elif text.startswith("also known as"):
            doc.props["aliases"] = core.unquote_items(text[len("also known as"):])
        else:
            raise core.PortraitError(
                "I do not know what '%s' means here" % word, number,
                hint="a portrait has role, met, currently, also known as, "
                     "observed, inferred, and contrast",
            )
        current = None

    return doc


def set_field(current, word, rest, number):
    if not rest:
        raise core.PortraitError("'%s' needs something after it" % word, number)

    if isinstance(current, Contrast) and word != "because":
        raise core.PortraitError(
            "'%s' does not belong to a contrast" % word, number,
            hint="a contrast only says why both rooms can be true",
        )

    if word == "when":
        current.when = rest
    elif word == "because":
        current.because = rest
    elif word == "on":
        if not core.DATE.match(rest):
            raise core.PortraitError(
                "'%s' is not a date" % rest, number,
                hint="dates look like 2026-03 or 2026-03-14",
            )
        current.on = rest
    elif word == "revised":
        if isinstance(current, Contrast):
            raise core.PortraitError("'revised' belongs to a claim, not a contrast",
                                number)
        parts = rest.split(None, 1)
        if not core.DATE.match(parts[0]):
            raise core.PortraitError(
                "'%s' is not a date" % parts[0], number,
                hint='write: revised 2026-05-09 "what changed your mind"',
            )
        note = parts[1].strip().strip('"') if len(parts) > 1 else ""
        current.revisions.append((parts[0], note))


# ---------------------------------------------------------------------------
# The laws both kinds enforce
# ---------------------------------------------------------------------------

def check_evidence(doc):
    warnings = []

    for claim in doc.claims:
        if claim.when is None:
            raise core.PortraitError(
                "'%s' has no room" % claim.trait, claim.line,
                hint="a person is not one thing everywhere. Say where it "
                     "holds:\n        when  at work, when the deadline "
                     "is clear",
            )
        if claim.because is None:
            raise core.PortraitError(
                "'%s' has no basis" % claim.trait, claim.line,
                hint="say what you actually saw, not what you concluded:\n"
                     "        because  finished the report at 2am without "
                     "complaining",
            )
        if claim.on is None:
            raise core.PortraitError(
                "'%s' is not dated" % claim.trait, claim.line,
                hint="add 'on 2026-03-14'. You will not remember when you "
                     "learned this, and the date is how you will find out "
                     "that you were wrong.",
            )

        if claim.kind == "inferred":
            lowered = claim.because.lower()
            for weak in WEAK_WORDS:
                if weak in lowered:
                    warnings.append(
                        "line %d: '%s' is inferred from a very small sample "
                        "(\"%s\"). Two times is not a pattern."
                        % (claim.line, claim.trait, weak)
                    )
                    break

    seen = set()
    for alias in doc.props.get("aliases", []):
        if alias in seen:
            raise core.PortraitError("'%s' is listed twice" % alias, doc.line)
        seen.add(alias)

    if "role" not in doc.props:
        warnings.append("line %d: no role given for %s" % (doc.line, doc.name))

    return warnings


# ---------------------------------------------------------------------------
# Writing, for the command line
# ---------------------------------------------------------------------------

def today():
    import datetime
    return datetime.date.today().isoformat()


def blank(name, role):
    """A brand new portrait with nothing in it yet."""
    return "remember %s\n\n    role            %s\n\nend\n" % (name, role)


def before_end(source, new_lines):
    """Put new lines immediately above the closing 'end'."""
    lines = source.rstrip("\n").split("\n")
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "end":
            return "\n".join(lines[:i] + new_lines + lines[i:]) + "\n"
    raise core.PortraitError(
        "this portrait has no 'end' to write before", len(lines),
        hint="add 'end' as the last line",
    )


def as_lines(kind, trait, room, evidence, date):
    return [
        "    %s %s" % (kind, trait),
        "        when      %s" % room,
        "        because   %s" % evidence,
        "        on        %s" % date,
        "",
    ]


def add_revision(source, line, date, note):
    """Insert a 'revised' line into the claim that begins at raw line `line`.

    By position, not by name. Two claims can share a name -- "reliable at
    work" and "reliable with family" are both legitimate -- and revising the
    wrong one because it happened to be first would be a silent corruption.
    """
    lines = source.rstrip("\n").split("\n")
    start = line - 1
    if not 0 <= start < len(lines):
        raise core.PortraitError("that claim is no longer in the file")
    word = lines[start].strip().split(None, 1)
    if not word or word[0] not in ("observed", "inferred"):
        raise core.PortraitError("that claim is no longer in the file")

    last = start
    indent = "        "
    i = start + 1
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == "":
            i += 1
            continue
        if stripped.split(None, 1)[0] in ("observed", "inferred", "contrast",
                                          "end"):
            break
        last = i
        indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
        i += 1

    new_line = '%srevised   %s "%s"' % (indent, date, note)
    return "\n".join(lines[:last + 1] + [new_line] + lines[last + 1:]) + "\n"


def summarise(doc):
    observed = [c for c in doc.claims if c.kind == "observed"]
    inferred = [c for c in doc.claims if c.kind == "inferred"]
    revisions = sum(len(c.revisions) for c in doc.claims)
    dates = [c.on for c in doc.claims if c.on] + \
            [d for c in doc.claims for d, _n in c.revisions]
    return {
        "observed": len(observed),
        "inferred": len(inferred),
        "claims": len(doc.claims),
        "revisions": revisions,
        "last": max(dates) if dates else "—",
    }
