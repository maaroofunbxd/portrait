# Start here

This is the how-to. `README.md` is the design document — read that later, or
never.

## Where it is

```
/Users/maaroofabdulkareem/Documents/deepseek-harness/default-workspace/portrait
```

Everything runs with `python3` on the Mac. Nothing to install.

## The four tools

```sh
python3 portrait.py add Ada              # answer four questions, get a claim
python3 portrait.py revise Ada           # record a change of mind
python3 portrait.py list                 # everyone, and how much
python3 portrait.py report Ada           # what it adds up to
```

That is the whole thing. The four tools underneath it — `remember.py`,
`understand.py`, `character.py`, `simulate.py` — still run on their own if you
want a specific one.

## Your first claim

There is no file to write by hand.  Answer four questions:

```sh
python3 portrait.py add Ada
```

```

  Ada — one claim.  Today is 2026-10-15.

  Who are they, in a word? (friend, colleague, ...) [friend]  colleague

  1) I saw it
  2) I worked it out
  Which?  1

  What is it, in a few words?  reliable
  Where does this hold?  a deadline has been agreed in advance
  What did you actually see?  sent the file two days early
  Date [2026-10-15]

  added.
  Ada now has 1 claim: 1 saw, 0 worked out, 0 revisions.
```

The file lands in `people/Ada.remember` and it is **checked before it is
written**. If the checker would refuse it, nothing is saved and you get the
reason instead.

Then, when something changes your mind:

```sh
python3 portrait.py revise Ada
```

```

  Claims about Ada:

    1) observed  reliable                 2026-10-15
    2) inferred  dislikes surprises       2026-10-15

  Which one?  2
  What changed your mind?  the quiet was about the flight
  Date [2026-10-15]

  revised.
```

And to see everyone you have:

```sh
python3 portrait.py list
```

```

  people/

    Ada           2 claims  1 revision   last 2026-10-15

  1 person, 2 claims, 1 revision.
```

`report Ada` gives you the long version.  `check Ada` if you want to know
whether the file is well formed.

**If you would rather write the file yourself**, that still works — copy
`examples/template.remember`, change the name, and fill it in.

## The three refusals you will hit first

The checker is not fussy about style. It is fussy about these, and it always
tells you the fix:

```
error: 'reliable' has no room

  a person is not one thing everywhere. Say where it holds:
        when  at work, when the deadline is clear
```

```
error: 'reliable' has no basis

  say what you actually saw, not what you concluded:
        because  finished the report at 2am without complaining
```

```
error: 'reliable' is not dated

  add 'on 2026-10-15'. You will not remember when you learned this, and the
  date is how you will find out that you were wrong.
```

Date it **today**. Not when the thing happened — when you noticed it. That is
the date you will want later.

## The habit

One claim, when you notice something. Not a journalling session.

When you see someone do something that tells you what they are like, open the
file and add four lines:

- **what** — `observed` if you saw it, `inferred` if you worked it out
- **when** — where was this true?
- **because** — what did you actually see?
- **on** — today

Then close it. That is the whole practice.

## What you get for it

Not immediately. In a year, `report` gives you this line:

```
  You have revised 1 of 1 inferences and 0 of 2 observations.
  Your observations have held up. Your inferences have not. Act accordingly.
```

That is the only thing here you cannot get any other way, and it takes a year
to become true. Everything else in this folder is scaffolding for that
sentence.

## The other three

- **`understand`** — when someone is genuinely two different people in two
  different places. It refuses to let you leave the contradiction unjoined.
- **`character`** — if you write fiction. Copy `examples/ada.character`.
- **`simulate`** — many agents, a few rules, a seed. Copy
  `examples/crowd.simulate`.

If you do not write fiction and do not model things, those two will sit
unused, and that is fine.

## The one limitation to know about

A `because` cannot wrap onto a second line. Keep it to one line, or the
parser will read the second line as a new instruction and complain.

## Tests

```sh
python3 tests/run_tests.py     # 28 checks, four tools
```
