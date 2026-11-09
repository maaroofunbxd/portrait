#!/usr/bin/env python3
"""
Tests for Portrait.

    python3 tests/run_tests.py

Four kinds of test:

  * portraits that should read clearly
  * portraits that should be refused, with the phrase the error must contain
  * reports that must say the thing they exist to say
  * a simulation that must give the same answer twice
"""

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PORTRAIT = os.path.join(ROOT, "portrait.py")
EXAMPLES = os.path.join(ROOT, "examples")
PYTHON = sys.executable


# Each kind as its own program, to prove they stand alone.
STANDALONE = [
    ("remember.py", "check", "ada.remember"),
    ("understand.py", "check", "ada.understand"),
    ("character.py", "check", "ada.character"),
    ("simulate.py", "check", "crowd.simulate"),
    ("remember.py", "report", "ada.remember"),
    ("understand.py", "report", "ada.understand"),
    ("character.py", "report", "ada.character"),
    ("simulate.py", "run", "crowd.simulate"),
]


# A program handed the wrong kind of portrait must say so.
WRONG_KIND = [
    ("remember.py", "ada.character"),
    ("remember.py", "ada.understand"),
    ("understand.py", "ada.remember"),
    ("character.py", "ada.remember"),
    ("simulate.py", "ada.understand"),
]


CLEAN = [
    "ada.remember",
    "ada.understand",
    "ada.character",
    "crowd.simulate",
]


REFUSALS = [
    ("errors/no_room.remember", "'patient' has no room"),
    ("errors/no_basis.remember", "'patient' has no basis"),
    ("errors/no_date.remember", "'patient' is not dated"),
    ("errors/unjoined.understand", "nothing joining them"),
    ("errors/unreasoned.character", "with no reason given"),
    ("errors/unseeded.simulate", "no seed"),
]


REPORTS = [
    ("ada.remember", "report", [
        "what you saw",
        "what you worked out",
        "You have revised 1 of 1 inferences and 0 of 2 observations",
    ]),
    ("ada.understand", "report", [
        "→ both hold",
        "1 trait, 1 of them holding differently",
    ]),
    ("ada.character", "report", [
        "breaks claustrophobic",
        "1 deliberate break",
    ]),
    ("crowd.simulate", "run", [
        "seed 12345",
        "turn 12",
        "exact output",
    ]),
]


def portrait(command, name):
    path = os.path.join(EXAMPLES, name)
    return subprocess.run(
        [PYTHON, PORTRAIT, command, path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )


def standalone(program, command, name):
    path = os.path.join(EXAMPLES, name)
    return subprocess.run(
        [PYTHON, os.path.join(ROOT, program), command, path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )


def cli(args, stdin, home):
    """Run portrait.py against a throwaway people directory."""
    env = dict(os.environ)
    env["PORTRAIT_HOME"] = home
    return subprocess.run(
        [PYTHON, PORTRAIT] + args,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        env=env,
    )


def check_cli(passed, failed):
    """The whole add -> add -> revise -> list loop, end to end."""
    home = tempfile.mkdtemp(prefix="portrait-test-")
    try:
        steps = [
            (["add", "Ada"],
             "colleague\n1\nreliable\nat work, deadline agreed\n"
             "sent the file early\n2026-01-01\n",
             "now has 1 claim"),
            (["add", "Ada"],
             "2\ndislikes surprises\nplans change\ngone quiet three times\n"
             "2026-02-02\n",
             "now has 2 claims"),
            (["revise", "Ada"],
             "2\nthe quiet was about the flight\n2026-03-03\n",
             "1 revision"),
            (["list", "Ada"], "", "Ada"),
            (["report", "Ada"], "", "You have revised 1 of 1 inferences"),
            (["check", "Ada"], "", "reads clearly"),
        ]
        for args, stdin, expect in steps:
            result = cli(args, stdin, home)
            if result.returncode != 0:
                failed += 1
                print("FAIL cli %s: exit %d\n%s"
                      % (" ".join(args), result.returncode, result.stderr))
                continue
            if expect not in result.stdout:
                failed += 1
                print("FAIL cli %s: expected %r\n%s"
                      % (" ".join(args), expect, result.stdout))
                continue
            passed += 1
            print("ok   cli: portrait.py %s" % " ".join(args))

        path = os.path.join(home, "Ada.remember")
        text = read_file(path)
        for phrase in ('observed reliable', 'inferred dislikes surprises',
                       'revised   2026-03-03'):
            if phrase not in text:
                failed += 1
                print("FAIL cli: the file is missing %r" % phrase)
                break
        else:
            passed += 1
            print("ok   cli: the file it wrote is well formed")

        # Two claims may share a name.  Revising must use the one you chose.
        dup = os.path.join(home, "Dup.remember")
        with open(dup, "w") as handle:
            handle.write(DUP)
        result = cli(["revise", "Dup"],
                     "2\nthe quiet was about the flight\n2026-03-03\n", home)
        text = read_file(dup)
        if result.returncode != 0:
            failed += 1
            print("FAIL cli: revise on a duplicated name failed\n%s"
                  % result.stderr)
        elif text.index("revised") > text.index("with family"):
            passed += 1
            print("ok   cli: revise uses the claim you chose, "
                  "not the first with that name")
        else:
            failed += 1
            print("FAIL cli: revise attached to the wrong claim\n%s" % text)
    finally:
        shutil.rmtree(home, ignore_errors=True)
    return passed, failed


DUP = """remember Dup

    role            friend

    observed reliable
        when      at work
        because   sent it early
        on        2026-01-01

    observed reliable
        when      with family
        because   showed up anyway
        on        2026-02-02

end
"""


def read_file(path):
    with open(path, "r") as opened:
        return opened.read()


def main():
    passed = 0
    failed = 0

    for program, command, name in STANDALONE:
        result = standalone(program, command, name)
        if result.returncode != 0 or not result.stdout:
            failed += 1
            print("FAIL %s %s %s: does not stand alone\n%s"
                  % (program, command, name, result.stderr))
            continue
        passed += 1
        print("ok   %s %s %s works on its own" % (program, command, name))

    for program, name in WRONG_KIND:
        result = standalone(program, "check", name)
        if result.returncode != 1 or "not a" not in result.stderr:
            failed += 1
            print("FAIL %s should refuse a portrait of the wrong kind (%s)"
                  % (program, name))
            continue
        passed += 1
        print("ok   %s refuses a portrait of the wrong kind" % program)

    for name in CLEAN:
        result = portrait("check", name)
        if result.returncode != 0:
            failed += 1
            print("FAIL %s: should read clearly\n%s" % (name, result.stderr))
            continue
        passed += 1
        print("ok   %s reads clearly" % name)

    for name, phrase in REFUSALS:
        result = portrait("check", name)
        if result.returncode != 1:
            failed += 1
            print("FAIL %s: expected a refusal, exit was %d"
                  % (name, result.returncode))
            continue
        if phrase not in result.stderr:
            failed += 1
            print("FAIL %s: refusal did not mention %r" % (name, phrase))
            print(result.stderr)
            continue
        passed += 1
        print("ok   %s is refused, and says why" % name)

    for name, command, phrases in REPORTS:
        result = portrait(command, name)
        missing = [p for p in phrases if p not in result.stdout]
        if missing:
            failed += 1
            print("FAIL %s %s: missing %r" % (name, command, missing))
            print(result.stdout)
            continue
        passed += 1
        print("ok   %s %s says the thing it exists to say" % (name, command))

    first = portrait("run", "crowd.simulate").stdout
    second = portrait("run", "crowd.simulate").stdout
    if first != second or not first:
        failed += 1
        print("FAIL crowd.simulate: the same seed gave two different answers")
    else:
        passed += 1
        print("ok   crowd.simulate gives the same answer twice")

    passed, failed = check_cli(passed, failed)

    print()
    print("%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
