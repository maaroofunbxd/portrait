# Portrait

A notation for writing down what you think you know about people.

**One notation, four checkers** — because there are four different ways to be
wrong about a person, and a checker can only check against something.

| Portrait | Ground truth | Wrong means | Checked against |
|---|---|---|---|
| `remember` | a real person | your model doesn't match them | **evidence** |
| `understand` | a real person | you flattened a contradiction into a single trait | **evidence, and whether contradictions are acknowledged** |
| `character` | your intent | they contradict themselves for no reason | **internal consistency** |
| `simulate` | the rules themselves | you can't get the same answer twice | **reproducibility** |

The four are separate files with the same syntax, on purpose. Mixing
`remember` and `character` in one file would be the oldest mistake in language
design: two different concepts wearing one notation. In `remember` a claim is
a *fallible belief*; in `character` it is a *decree*. If they shared a file
you could no longer tell which one you were reading.

---

## Four tools, one engine

I first built this as a single file with four modes. That was the fastest way
to show all four in one sitting, and it was the wrong architecture.

The honest accounting of what the kinds share:

| | Shared with the others |
|---|---|
| `remember` + `understand` | **the model and the laws** — a claim with a room, a basis and a date |
| `character` | a way of reading lines, and the error format |
| `simulate` | a way of reading lines, and the error format |

So there is one engine for the pair that genuinely shares semantics, and
nothing shared between the rest. Four tools, four names that match the four
concepts you think in:

```
claims.py        the shared model and laws -- NOT a tool, never run
remember.py      remember            -> checked against evidence
understand.py    understand          -> evidence + acknowledged contradictions
character.py     character           -> internal consistency
simulate.py      simulate            -> reproducibility
portrait.py      a dispatcher; reads the first word and delegates
```

`understand` is `remember` plus exactly one rule, and that rule lives in
`understand.py` rather than in the shared engine, because it is this tool's
rule and not the other one's:

> a trait claimed in two different rooms must be joined by a contrast, or the
> two claims quietly merge into one false one.

Each tool runs on its own:

```sh
python3 remember.py   check  examples/ada.remember
python3 understand.py report examples/ada.understand
python3 character.py  report examples/ada.character
python3 simulate.py   run    examples/crowd.simulate
```

And each refuses the others, which is what makes them tools rather than
modes:

```
$ python3 remember.py check examples/ada.understand
examples/ada.understand: error: this is an understand portrait, not a remember one
```

Even the vocabulary is separated. `contrast` is an `understand` word, and a
`remember` file that uses one is refused:

```
$ python3 remember.py check my.remember
my.remember: error: 'contrast' belongs to an understand portrait
```

`portrait.py` exists only so you do not have to remember which one to call.
It does no work itself.

**Why this matters beyond tidiness:** these are meant to be kept. If
`simulate` has a bug, fixing it should not change a single byte of the tool
you have been using to remember people for a decade. Small and frozen beats
unified. That is channel 14 -- version drift -- applied to my own program.
---

## The laws every portrait obeys

**A trait with no room is a trait that will mislead you.** Every claim says
where it holds. There is no decontextualised claim about a person — that is
the fundamental attribution error, and here it is a compile error.

**Everything is dated.** You will not remember when you learned it, and the
date is the only way to find out later that you were wrong.

**A person is one thing with many names, never several copies.** Aliases are
aliases.

**Nothing is erased.** A claim can be revised; the revision is kept.

---

## `remember` — a record kept for years

```
remember Ada

    role            friend
    also known as   "A", "Ada L"
    met             2019-04
    currently       travelling, tired

    observed patient
        when      the work has a clear deadline
        because   finished the report at 2am without complaining
        on        2026-03-14

    inferred dislikes surprises
        when      plans change without warning
        because   went quiet, twice
        on        2026-05-02
        revised   2026-05-09 "the quiet was about the flight, not the plans"

end
```

The checker refuses a claim with no room, no basis, or no date:

```
error: 'patient' has no room

  at line 8
          observed patient

  a person is not one thing everywhere. Say where it holds:
        when  at work, when the deadline is clear
```

```
error: 'patient' has no basis

  say what you actually saw, not what you concluded:
        because  finished the report at 2am without complaining
```

```
error: 'patient' is not dated

  add 'on 2026-03-14'. You will not remember when you learned this, and the
  date is how you will find out that you were wrong.
```

And it warns when an inference rests on almost nothing:

```
warning: line 24: 'dislikes surprises' is inferred from a very small sample
("twice"). Two times is not a pattern.
```

### The report

This is the part that makes it worth keeping. It is not a model of Ada. It is
a model of **your model of Ada**:

```
$ python3 portrait.py report examples/ada.remember

Ada — remember

  role       friend
  met        2019-04
  now        travelling, tired

  3 claims   (2 observed, 1 inferred)

  what you saw
    patient                    2026-03-14
      when     the work has a clear deadline
      because  finished the report at 2am without complaining
    generous                   2025-11-02
      when     someone else is short
      because   covered the bill twice without mentioning it

  what you worked out
    dislikes surprises         2026-05-02
      when     plans change without warning
      because  went quiet, twice
      revised 2026-05-09  the quiet was about the flight, not the plans

  You have revised 1 of 1 inferences and 0 of 2 observations.
  Your observations have held up. Your inferences have not. Act accordingly.
```

---

## `understand` — she is not one thing

Same syntax. The difference is the checker's second question: **a trait
claimed in two different rooms must be joined, not left ambiguous.**

```
understand Ada

    observed patient
        when      at work, with a shared deadline
        because   stayed late to finish the report with the team
        on        2026-03-14

    observed patient
        when      at home, when plans change
        because   went quiet and left the room
        on        2026-04-02

    contrast patient
        because   at work the deadline is shared, so waiting is shared
                  too; at home it is hers alone, and a change takes it away

end
```

Leave the contrast out and it refuses:

```
error: 'patient' is claimed in two different rooms with nothing joining them

  both can be true. Say so, and say why:
        contrast patient
            because  ...
```

Here contradiction is data, not a mistake to be smoothed over. The report
shows the shape:

```
  patient
    at work, with a shared deadline        observed  2026-03-14
    at home, when plans change             observed  2026-04-02
    → both hold: at work the deadline is shared, ...
```

---

## `character` — a person who does not exist

There is no ground truth here, so the checker asks a different question: **if
she acts against her own nature, is the reason on the page?**

```
character Ada

    trait claustrophobic
        when      in small enclosed spaces

    scene the-lift
        does      steps into the lift and rides it to the ninth floor
        against   claustrophobic
        because   she has decided the fear is a luxury she cannot afford

    scene the-letter
        does      reads the letter twice, then drives four hours
        shows     loyal

end
```

```
error: this scene breaks 'claustrophobic' with no reason given

  a character who breaks their own nature needs a reason on the page:
        because  she is dissociating
```

It also warns you about craft problems you can't see yourself:

```
warning: line 11: 'claustrophobic' is established but never shown in a scene
```

---

## `simulate` — many people interacting

Different question again: **could you get this answer twice?**

```
simulate crowd

    seed 12345

    agents shopper count 20
        patience starts at 10

    each turn
        every shopper loses 1 patience
        chance 1 in 6 : a shopper leaves

    run 12 turns

end
```

```
error: this simulation has no seed

  without a seed you cannot get the same answer twice, and then it is not a
  model, it is an anecdote.
        seed 12345
```

```
$ python3 portrait.py run examples/crowd.simulate

crowd — simulate

  seed 12345

  turn  0   shopper 20/20   patience 10
  turn  1  shopper 18/20   patience 9
  ...
  turn 12  shopper 1/20   patience -2
```

Run it again and you get that exact output, because the seed is written down.

---

## What this does not do

Stated plainly, because a tool that oversells itself is worse than one that
does less:

- **`character` cannot detect a *silent* break.** It can only check that a
  break you marked has a reason. Noticing that a scene contradicts a trait
  without being told would require understanding the prose.
- **`understand` is syntactic.** It triggers on the same trait name in two
  rooms. It cannot see that `patient` and `impatient` are opposites, because
  it does not know what words mean.
- **`simulate` is tiny.** Numeric properties, additive rules, and a leaving
  chance. No conditionals, no agent-to-agent interaction.
- **The syntax is line-based.** A `because` clause cannot wrap across lines.
  That is a real cost, and it is the price of keeping the grammar obvious.
- **Nothing here checks whether your claims are true.** It checks that you
  wrote them down honestly — with a room, a basis, and a date. Whether you
  were right is not a thing a file can know.

---

## Using it

Four tools, plus a dispatcher if you do not want to remember which to call:

```sh
python3 remember.py   check  examples/ada.remember     # a real person
python3 understand.py report examples/ada.understand   # the same, in two rooms
python3 character.py  report examples/ada.character    # someone invented
python3 simulate.py   run    examples/crowd.simulate   # many at once

python3 portrait.py check examples/ada.remember        # same thing, delegated
python3 tests/run_tests.py                             # 28 tests
```

A portrait begins with `remember`, `understand`, `character`, or `simulate`,
and ends with `end`. `examples/` holds one of each. `examples/errors/` holds
six that are refused, each written to show what the refusal reads like.
