#!/usr/bin/env python3
"""
remember
========
A record of a real person, kept for years.

    python3 remember.py check  examples/ada.remember
    python3 remember.py report examples/ada.remember

Checked against: evidence.

The laws live in claims.py, because `understand` enforces the same ones. What
lives here is the report — what you saw, what you worked out, and how often
you had to take the second one back.
"""

import sys

import claims
import core

COMMANDS = ("check", "report")

USAGE = """remember

  python3 remember.py check  path/to/file
  python3 remember.py report path/to/file

A record of someone real. Every claim needs a room, a basis and a date.
"""


def report(doc):
    out = ["%s — remember" % doc.name, ""]
    for key, label in (("role", "role"), ("aliases", "aliases"),
                       ("met", "met"), ("currently", "now")):
        if key not in doc.props:
            continue
        value = doc.props[key]
        if key == "aliases":
            value = ", ".join('"%s"' % a for a in value)
        out.append("  %-10s %s" % (label, value))
    out.append("")

    observed = [c for c in doc.claims if c.kind == "observed"]
    inferred = [c for c in doc.claims if c.kind == "inferred"]
    out.append("  %d claim%s   (%d observed, %d inferred)"
               % (len(doc.claims), "" if len(doc.claims) == 1 else "s",
                  len(observed), len(inferred)))
    out.append("")

    for label, group in (("what you saw", observed),
                         ("what you worked out", inferred)):
        if not group:
            continue
        out.append("  %s" % label)
        for claim in group:
            out.append("    %-26s %s" % (claim.trait, claim.on))
            out.append("      when     %s" % claim.when)
            out.append("      because  %s" % claim.because)
            for date, note in claim.revisions:
                out.append("      revised %s  %s" % (date, note))
        out.append("")

    revised_in = sum(1 for c in inferred if c.revisions)
    revised_ob = sum(1 for c in observed if c.revisions)

    if not inferred:
        out.append("  You have written down %d observation%s and nothing you "
                   "worked out."
                   % (len(observed), "" if len(observed) == 1 else "s"))
        out.append("  This line compares the two, so it stays empty until "
                   "both exist.")
    else:
        out.append("  You have revised %d of %d inferences and %d of %d "
                   "observations."
                   % (revised_in, len(inferred), revised_ob, len(observed)))
        if revised_in and observed and not revised_ob:
            out.append("  Your observations have held up. Your inferences "
                       "have not. Act accordingly.")
        elif not revised_in and not revised_ob:
            out.append("  Nothing has been revised yet. That is what early "
                       "looks like -- the first revision is the one that "
                       "makes this line worth reading.")
    return "\n".join(out).rstrip()


def handle(command, path, source):
    doc = claims.parse(source, "remember")
    warnings = claims.check_evidence(doc)

    for warning in warnings:
        sys.stderr.write("%s: warning: %s\n" % (path, warning))

    if command == "check":
        note = ", with the notes above" if warnings else ""
        print("%s: reads clearly (a remember portrait)%s" % (path, note))
    else:
        print(report(doc))
    return 0


def main(argv):
    return core.run(argv, COMMANDS, handle, USAGE)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
