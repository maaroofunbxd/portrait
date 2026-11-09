#!/usr/bin/env python3
"""
portrait
========
The one command.

    python3 portrait.py add    [Name]        answer four questions, get a claim
    python3 portrait.py revise [Name]        record that you changed your mind
    python3 portrait.py list                 everyone you have, and how much
    python3 portrait.py report <Name|file>   what it adds up to
    python3 portrait.py check  <Name|file>   is it written properly
    python3 portrait.py run    <Name|file>   play a simulation out

`add` and `revise` write into `people/`.  Everything else takes either a
person's name or a path to a file.

A claim is one atomic thing appended to one file, so unlike a program there
is nothing to lose by typing it at a prompt.  That is why this exists here
and not for Plain.
"""

import os
import sys

import claims
import core
import remember
import understand
import character
import simulate

HANDLERS = {
    "remember": remember,
    "understand": understand,
    "character": character,
    "simulate": simulate,
}

# Where `add` and `revise` write.  Set PORTRAIT_HOME to keep them elsewhere.
PEOPLE = os.environ.get("PORTRAIT_HOME") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "people")
EXTENSIONS = (".remember", ".understand", ".character", ".simulate")

USAGE = """Portrait

  python3 portrait.py add    [Name]        add one claim
  python3 portrait.py revise [Name]        record a change of mind
  python3 portrait.py list                 everyone, and how much
  python3 portrait.py report <Name|file>   what it adds up to
  python3 portrait.py check  <Name|file>   is it written properly
  python3 portrait.py run    <Name|file>   play a simulation out

  add and revise write into people/.  Report, check and run take a name
  (Ada) or a path (people/Ada.remember).
"""


# ---------------------------------------------------------------------------
# Asking
# ---------------------------------------------------------------------------

def ask(prompt, default=None):
    """One question.  Empty input takes the default, or asks again."""
    suffix = " [%s]" % default if default else ""
    tty = sys.stdin.isatty()
    while True:
        if tty:
            # A real terminal: the prompt sits on the line you type into.
            lead = "  %s%s  " % (prompt, suffix)
        else:
            # Piped or captured: the question on its own line, read silently.
            print()
            print("  %s%s" % (prompt, suffix))
            lead = ""
        try:
            answer = input(lead).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if answer:
            return answer
        if default is not None:
            return default


def give_up():
    print("\n  nothing written.")
    return 1


# ---------------------------------------------------------------------------
# Where people live
# ---------------------------------------------------------------------------

def person_path(name):
    return os.path.join(PEOPLE, name + ".remember")


def resolve(argument):
    """A path if it is one, else a person -- by filename, then by the name
    written inside the file."""
    if os.path.exists(argument):
        return argument
    for extension in EXTENSIONS:
        candidate = os.path.join(PEOPLE, argument + extension)
        if os.path.exists(candidate):
            return candidate

    matches = []
    for path, _label in portrait_files():
        try:
            _kind, name, _body = core.header(read(path))
        except core.PortraitError:
            continue
        if name == argument:
            matches.append(path)

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise core.PortraitError(
            "more than one portrait calls itself '%s'" % argument, None,
            hint="they are: "
                 + ", ".join(os.path.basename(m) for m in matches)
                 + ". Give a path instead, or change the name on their "
                   "first line.",
        )
    return None


def read(path):
    with open(path, "r") as opened:
        return opened.read()


def mode_of(source):
    kind, _name, _body = core.header(source)
    return kind


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------

def command_add(name):
    path = person_path(name)
    fresh = not os.path.exists(path)
    os.makedirs(PEOPLE, exist_ok=True)

    print()
    print("  %s — one claim.  Today is %s." % (name, claims.today()))

    role = None
    if fresh:
        role = ask("Who are they, in a word? (friend, colleague, ...)", "friend")
        if role is None:
            return give_up()

    print()
    print("  1) I saw it")
    print("  2) I worked it out")
    kind = None
    while kind is None:
        answer = ask("Which?")
        if answer is None:
            return give_up()
        if answer in ("1", "o", "observed"):
            kind = "observed"
        elif answer in ("2", "i", "inferred"):
            kind = "inferred"
        else:
            print("  Type 1 or 2.")

    trait = ask("What is it, in a few words?")
    if trait is None:
        return give_up()

    room = ask("Where does this hold?")
    if room is None:
        return give_up()

    if kind == "observed":
        evidence = ask("What did you actually see?")
    else:
        evidence = ask("What have you seen that made you think so, "
                       "and how many times?")
    if evidence is None:
        return give_up()

    date = ask("Date", claims.today())
    if date is None:
        return give_up()

    if fresh:
        source = claims.blank(name, role)
    else:
        source = read(path)

    source = claims.before_end(
        source, claims.as_lines(kind, trait, room, evidence, date))

    return write(path, source, "added")


def command_revise(name):
    path = person_path(name)
    if not os.path.exists(path):
        print("\n  there is no portrait for %s yet." % name)
        print("  start one with:  python3 portrait.py add %s" % name)
        return 1

    source = read(path)
    doc = claims.parse(source, mode_of(source))
    if not doc.claims:
        print("\n  %s has no claims to revise yet." % name)
        return 1

    print()
    print("  Claims about %s:" % name)
    print()
    for index, claim in enumerate(doc.claims, 1):
        print("    %d) %-9s %-24s %s" % (index, claim.kind, claim.trait,
                                         claim.on))
    print()

    chosen = None
    while chosen is None:
        answer = ask("Which one?")
        if answer is None:
            return give_up()
        if answer.isdigit() and 1 <= int(answer) <= len(doc.claims):
            chosen = doc.claims[int(answer) - 1]
        else:
            print("  Type a number from 1 to %d." % len(doc.claims))

    note = ask("What changed your mind?")
    if note is None:
        return give_up()

    date = ask("Date", claims.today())
    if date is None:
        return give_up()

    source = claims.add_revision(source, chosen.line, date, note)
    return write(path, source, "revised")


def write(path, source, verb):
    """Check before writing.  A refused file never reaches the disk."""
    try:
        kind = mode_of(source)
        doc = claims.parse(source, kind) if kind in ("remember",
                                                     "understand") else None
        warnings = claims.check_evidence(doc) if doc else []
    except core.PortraitError as err:
        sys.stderr.write(core.render_error(err, source, path) + "\n")
        return 1

    with open(path, "w") as opened:
        opened.write(source)

    print()
    print("  %s." % verb)
    if doc is not None:
        counts = claims.summarise(doc)
        print("  %s now has %d claim%s: %d saw, %d worked out, %d revision%s."
              % (doc.name, counts["claims"],
                 "" if counts["claims"] == 1 else "s",
                 counts["observed"], counts["inferred"], counts["revisions"],
                 "" if counts["revisions"] == 1 else "s"))
    for warning in warnings:
        print("  note: %s" % warning)
    print("  %s" % path)
    return 0


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def portrait_files():
    """Every portrait we can find -- in people/, and next to the scripts.

    The second one is so files made before `people/` existed still show up.
    Nothing is moved.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    found = []
    seen = set()
    for directory, label in ((PEOPLE, "people/"), (here, "here")):
        if not os.path.isdir(directory):
            continue
        for filename in sorted(os.listdir(directory)):
            if not filename.endswith(EXTENSIONS):
                continue
            path = os.path.join(directory, filename)
            if path in seen:
                continue
            seen.add(path)
            found.append((path, label))
    return found


def command_list():
    files = portrait_files()
    if not files:
        print("\n  nobody yet.")
        print("  start with:  python3 portrait.py add Ada")
        return 0

    by_place = {}
    for path, label in files:
        by_place.setdefault(label, []).append(path)

    total_claims = total_revisions = counted = 0
    for label in ("people/", "here"):
        if label not in by_place:
            continue
        print()
        print("  %s" % (os.path.relpath(PEOPLE) + "/" if label == "people/"
                        else "next to the scripts"))
        print()
        for path in by_place[label]:
            filename = os.path.basename(path)
            try:
                source = read(path)
                kind = mode_of(source)
                if kind in ("remember", "understand"):
                    doc = claims.parse(source, kind)
                    counts = claims.summarise(doc)
                    line = ("    %-16s %2d claim%s  %d revision%s   last %s"
                            % (filename, counts["claims"],
                               "" if counts["claims"] == 1 else "s",
                               counts["revisions"],
                               "" if counts["revisions"] == 1 else "s",
                               counts["last"]))
                    if filename != doc.name + ".remember":
                        line += "   (calls itself %s)" % doc.name
                    print(line)
                    total_claims += counts["claims"]
                    total_revisions += counts["revisions"]
                    counted += 1
                else:
                    print("    %-12s a %s portrait" % (filename, kind))
            except core.PortraitError as err:
                print("    %-12s needs attention: %s" % (filename,
                                                         err.message))

    print()
    print("  %d %s, %d claim%s, %d revision%s."
          % (counted, "person" if counted == 1 else "people",
             total_claims, "" if total_claims == 1 else "s",
             total_revisions, "" if total_revisions == 1 else "s"))
    return 0


# ---------------------------------------------------------------------------
# check / report / run
# ---------------------------------------------------------------------------

def command_on(command, argument):
    try:
        path = resolve(argument)
    except core.PortraitError as err:
        sys.stderr.write("error: %s\n" % err.message)
        if err.hint:
            sys.stderr.write("  %s\n" % err.hint)
        return 1

    if path is None:
        print("\n  there is no portrait for '%s'." % argument)
        print("  start one with:  python3 portrait.py add %s" % argument)
        return 1

    source = read(path)
    try:
        kind, _name, _body = core.header(source)
        module = HANDLERS[kind]
        if command not in module.COMMANDS:
            sys.stderr.write(
                "%s: error: a %s portrait has no '%s'; try %s\n"
                % (path, kind, command, " or ".join(module.COMMANDS)))
            return 1
        return module.handle(command, path, source)
    except core.PortraitError as err:
        sys.stderr.write(core.render_error(err, source, path) + "\n")
        return 1


# ---------------------------------------------------------------------------

def main(argv):
    if len(argv) < 2:
        sys.stderr.write(USAGE)
        return 2

    command = argv[1]
    argument = argv[2] if len(argv) > 2 else None

    if command == "list":
        return command_list()

    if command == "add":
        if argument is None:
            argument = ask("Who?")
            if argument is None:
                return give_up()
        return command_add(argument)

    if command == "revise":
        if argument is None:
            argument = ask("Who?")
            if argument is None:
                return give_up()
        return command_revise(argument)

    if command in ("check", "report", "run"):
        if argument is None:
            sys.stderr.write(USAGE)
            return 2
        return command_on(command, argument)

    sys.stderr.write(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
