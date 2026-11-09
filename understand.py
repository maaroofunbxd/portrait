#!/usr/bin/env python3
"""
understand
==========
The same person, but the point is that they are not one thing.

    python3 understand.py check  examples/ada.understand
    python3 understand.py report examples/ada.understand

Checked against: evidence, and whether contradictions have been acknowledged.

This is `remember` plus exactly one rule, and the rule lives here rather than
in claims.py, because it is this tool's rule and not the other one's:

    a trait claimed in two different rooms must be joined by a contrast,
    or the two claims will quietly merge into one false one.
"""

import sys

import claims
import core

COMMANDS = ("check", "report")

USAGE = """understand

  python3 understand.py check  path/to/file
  python3 understand.py report path/to/file

The same person in more than one room. A trait that holds differently in two
places must be joined by a contrast, or you have flattened them into one.
"""


def check_contrasts(doc):
    """A trait claimed in two rooms must be joined, not left ambiguous."""
    joined = {c.trait for c in doc.contrasts}

    for contrast in doc.contrasts:
        if contrast.because is None:
            raise core.PortraitError(
                "'contrast %s' does not say why both hold" % contrast.trait,
                contrast.line,
                hint="write: because  the room decides, and both rooms are "
                     "real",
            )
        if not doc.claims_for(contrast.trait):
            raise core.PortraitError(
                "'%s' is contrasted but never claimed" % contrast.trait,
                contrast.line,
            )

    for claim in doc.claims:
        rooms = {c.when for c in doc.claims_for(claim.trait)}
        if len(rooms) > 1 and claim.trait not in joined:
            raise core.PortraitError(
                "'%s' is claimed in two different rooms with nothing "
                "joining them" % claim.trait, claim.line,
                hint="both can be true. Say so, and say why:\n"
                     "        contrast %s\n"
                     "            because  ..." % claim.trait,
            )


def report(doc):
    out = ["%s — understand" % doc.name, ""]
    joined = {c.trait: c for c in doc.contrasts}

    traits = []
    for claim in doc.claims:
        if claim.trait not in traits:
            traits.append(claim.trait)
    traits.sort()

    for trait in traits:
        out.append("  %s" % trait)
        for claim in doc.claims_for(trait):
            out.append("    %-38s %s  %s"
                       % (claim.when, claim.kind, claim.on))
        if trait in joined:
            out.append("    → both hold: %s" % joined[trait].because)
        out.append("")

    out.append("  %d trait%s, %d of them holding differently in different "
               "rooms." % (len(traits), "" if len(traits) == 1 else "s",
                           len(joined)))
    return "\n".join(out).rstrip()


def handle(command, path, source):
    doc = claims.parse(source, "understand")
    warnings = claims.check_evidence(doc)
    check_contrasts(doc)

    for warning in warnings:
        sys.stderr.write("%s: warning: %s\n" % (path, warning))

    if command == "check":
        note = ", with the notes above" if warnings else ""
        print("%s: reads clearly (an understand portrait)%s" % (path, note))
    else:
        print(report(doc))
    return 0


def main(argv):
    return core.run(argv, COMMANDS, handle, USAGE)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
