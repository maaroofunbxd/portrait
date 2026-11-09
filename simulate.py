#!/usr/bin/env python3
"""
simulate
========
Many people interacting.

    python3 simulate.py check  examples/crowd.simulate
    python3 simulate.py report examples/crowd.simulate
    python3 simulate.py run    examples/crowd.simulate

A third kind of ground truth again.  Nobody is being remembered and nobody is
being written; the question is whether you can get the same answer twice.

Checked against: reproducibility.
"""

import random
import re
import sys

import core
from core import PortraitError

COMMANDS = ("check", "report", "run")

USAGE = """simulate

  python3 simulate.py check  path/to/file
  python3 simulate.py report path/to/file
  python3 simulate.py run    path/to/file

Many agents, a few rules, a seed. Without the seed you cannot get the same
answer twice, and then it is not a model.
"""

AGENTS = re.compile(r"\Aagents\s+(\S+)\s+count\s+(\d+)\Z")
STARTS = re.compile(r"\A(\S+)\s+starts at\s+(-?\d+(?:\.\d+)?)\Z")
ADJUST = re.compile(r"\Aevery\s+(\S+)\s+(loses|gains)\s+"
                    r"(\d+(?:\.\d+)?)\s+(\S+)\Z")
CHANCE = re.compile(r"\Achance\s+(\d+)\s+in\s+(\d+)\s*:\s*"
                    r"a\s+(\S+)\s+leaves\Z")
RUN = re.compile(r"\Arun\s+(\d+)\s+turns?\Z")


# ---------------------------------------------------------------------------
# The model
# ---------------------------------------------------------------------------

class Rule:
    def __init__(self, kind, line):
        self.kind = kind          # adjust | chance
        self.line = line
        self.agent = None
        self.direction = None
        self.amount = None
        self.property = None
        self.numerator = None
        self.denominator = None


class Portrait:
    def __init__(self, name, line):
        self.mode = "simulate"
        self.name = name
        self.line = line
        self.seed = None
        self.agent_kinds = {}
        self.agent_order = []
        self.rules = []
        self.turns = None


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def parse(source):
    mode, name, body = core.header(source)
    if mode != "simulate":
        raise PortraitError(
            "this is a %s portrait, not a simulation" % mode, 1,
            hint="simulate.py only reads portraits that begin with 'simulate'",
        )
    core.require_end(body)

    doc = Portrait(name, 1)
    current_kind = None
    in_turn = False

    for number, text in body:
        if text == "end":
            break

        if text == "each turn":
            in_turn = True
            current_kind = None
            continue

        if text.startswith("seed"):
            value = text[4:].strip()
            if not value.isdigit():
                raise PortraitError("the seed must be a whole number", number,
                                    hint="write: seed 12345")
            doc.seed = int(value)
            continue

        match = AGENTS.match(text)
        if match:
            kind, count = match.group(1), int(match.group(2))
            if kind in doc.agent_kinds:
                raise PortraitError("'%s' is declared twice" % kind, number)
            doc.agent_kinds[kind] = {"count": count, "props": {}}
            doc.agent_order.append(kind)
            current_kind = kind
            in_turn = False
            continue

        match = STARTS.match(text)
        if match and current_kind is not None and not in_turn:
            doc.agent_kinds[current_kind]["props"][match.group(1)] = float(
                match.group(2))
            continue

        match = ADJUST.match(text)
        if match:
            rule = Rule("adjust", number)
            rule.agent = match.group(1)
            rule.direction = match.group(2)
            rule.amount = float(match.group(3))
            rule.property = match.group(4)
            doc.rules.append(rule)
            continue

        match = CHANCE.match(text)
        if match:
            rule = Rule("chance", number)
            rule.numerator = int(match.group(1))
            rule.denominator = int(match.group(2))
            rule.agent = match.group(3)
            doc.rules.append(rule)
            continue

        match = RUN.match(text)
        if match:
            doc.turns = int(match.group(1))
            continue

        raise PortraitError(
            "I do not know what '%s' means here" % text, number,
            hint="a simulation has seed, agents, each turn, and run",
        )

    return doc


# ---------------------------------------------------------------------------
# Checking
# ---------------------------------------------------------------------------

def check(doc):
    warnings = []

    if doc.seed is None:
        raise PortraitError(
            "this simulation has no seed", doc.line,
            hint="without a seed you cannot get the same answer twice, and "
                 "then it is not a model, it is an anecdote.\n"
                 "        seed 12345",
        )
    if doc.turns is None:
        raise PortraitError("this simulation never runs", doc.line,
                            hint="add: run 10 turns")
    if not doc.agent_kinds:
        raise PortraitError("this simulation has no agents", doc.line)

    for rule in doc.rules:
        if rule.agent not in doc.agent_kinds:
            raise PortraitError(
                "'%s' is not a kind of agent here" % rule.agent, rule.line,
                hint="the kinds are: " + ", ".join(doc.agent_order),
            )
        if rule.kind == "adjust":
            known = doc.agent_kinds[rule.agent]["props"]
            if rule.property not in known:
                raise PortraitError(
                    "'%s' has no property called '%s'"
                    % (rule.agent, rule.property), rule.line,
                    hint="its properties are: "
                         + (", ".join(sorted(known)) if known else "none"),
                )
        if rule.kind == "chance" and rule.denominator == 0:
            raise PortraitError("'in 0' is not a chance", rule.line)
        if rule.kind == "chance" and rule.numerator > rule.denominator:
            warnings.append(
                "line %d: a %d in %d chance is more than certain"
                % (rule.line, rule.numerator, rule.denominator)
            )

    for kind in doc.agent_order:
        if not doc.agent_kinds[kind]["props"]:
            warnings.append(
                "line %d: '%s' has no properties, so nothing can change "
                "about it" % (doc.line, kind)
            )
    return warnings


# ---------------------------------------------------------------------------
# Reporting and running
# ---------------------------------------------------------------------------

def trim(value):
    if value == int(value):
        return str(int(value))
    return repr(value)


def report(doc):
    out = ["%s — simulate" % doc.name, ""]
    out.append("  seed   %d" % doc.seed)
    for kind in doc.agent_order:
        spec = doc.agent_kinds[kind]
        props = ", ".join("%s %s" % (k, trim(v))
                          for k, v in sorted(spec["props"].items()))
        out.append("  %-10s %d agents%s"
                   % (kind, spec["count"],
                      ("  (" + props + ")") if props else ""))
    out.append("")
    out.append("  each turn")
    for rule in doc.rules:
        if rule.kind == "adjust":
            out.append("    every %s %s %s %s"
                       % (rule.agent, rule.direction, trim(rule.amount),
                          rule.property))
        else:
            out.append("    chance %d in %d : a %s leaves"
                       % (rule.numerator, rule.denominator, rule.agent))
    out.append("  run %d turns" % doc.turns)
    return "\n".join(out).rstrip()


def play(doc):
    """Play the simulation out.  Same seed, same answer, every time."""
    rng = random.Random(doc.seed)
    agents = []
    for kind in doc.agent_order:
        spec = doc.agent_kinds[kind]
        for _ in range(spec["count"]):
            agents.append({"kind": kind, "alive": True,
                           "props": dict(spec["props"])})

    out = ["%s — simulate" % doc.name, ""]
    out.append("  seed %d" % doc.seed)
    out.append("")
    out.append("  turn  0   %s" % tally(agents, doc.agent_order))

    for turn in range(1, doc.turns + 1):
        for rule in doc.rules:
            if rule.kind == "adjust":
                for agent in agents:
                    if agent["alive"] and agent["kind"] == rule.agent:
                        if rule.direction == "loses":
                            agent["props"][rule.property] -= rule.amount
                        else:
                            agent["props"][rule.property] += rule.amount
            else:
                for agent in agents:
                    if (agent["alive"] and agent["kind"] == rule.agent
                            and rng.randint(1, rule.denominator)
                            <= rule.numerator):
                        agent["alive"] = False
        out.append("  turn %2d  %s" % (turn, tally(agents, doc.agent_order)))

    out.append("")
    out.append("  Run it again: the seed is written down, so you get this "
               "exact output.")
    return "\n".join(out)


def tally(agents, order):
    parts = []
    for kind in order:
        group = [a for a in agents if a["kind"] == kind]
        alive = [a for a in group if a["alive"]]
        chunk = "%s %d/%d" % (kind, len(alive), len(group))
        for name in sorted(group[0]["props"]) if group else []:
            if alive:
                mean = sum(a["props"][name] for a in alive) / len(alive)
                chunk += "   %s %s" % (name, trim(round(mean, 1)))
        parts.append(chunk)
    return "   ".join(parts)


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
        print("%s: reads clearly (a simulate portrait)%s" % (path, note))
    elif command == "report":
        print(report(doc))
    else:
        print(play(doc))
    return 0


def main(argv):
    return core.run(argv, COMMANDS, handle, USAGE)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
