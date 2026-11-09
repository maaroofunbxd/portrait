# The workflow

The tool is built. This is how to actually run it, so it does not become a
folder you stopped opening.

Three loops. Four rules. One first session.

---

## The three loops

### Loop 1 — Capture

**Trigger:** you noticed something. Specifically, one of these two:

- someone did something you did not expect
- you caught yourself concluding something about them

**Action:** `python3 portrait.py add Ada`. Four answers. Today's date.
Two minutes.

**Then close the file.**

That last line is the discipline. Capture is not journalling. If you find
yourself writing a paragraph, you are doing it wrong — and the parser will
stop you anyway, because a `because` cannot wrap.

### Loop 2 — Consult

**Trigger:** you are about to do something that depends on your read of them.
Tell them something, ask them for something, trust them with something.

**Action:** `python3 portrait.py report Ada`. Thirty seconds. Look for one
thing:

> Is what I am about to act on **observed** or **inferred** — and how old
> is it?

That is the whole question. Acting on a two-year-old inference is how you
treat someone as who they were.

### Loop 3 — Review

**Trigger:** monthly. Put it somewhere you will trip over it.

**Action:** `python3 portrait.py list`, then `report` on each. Ten minutes
total. Three things to look for:

1. **Inferences with no revision and no recent observation.** These are
   untested. You are still running on them.
2. **Inferences you have revised.** These are the payment. This is where the
   calibration comes from.
3. **Clusters of dates.** If every claim about someone being "impatient" is
   dated in one bad fortnight, you have recorded March, not a person. The
   `on` field is the only reason you can see this, and you cannot see it in
   your head.

---

## The four rules

**1. An observation is what a camera would have recorded.**

```
observed late
    when      meetings with a fixed start time
    because   arrived 20 minutes after the agreed time, no message
    on        2026-10-15
```

Not *"didn't care about my time"* — that is already an inference. Behaviour
is observable. Motive is not.

This is why observations hold up and inferences don't: an observation is a
report of an event, and an inference is a claim about a person.

**2. One event, one claim.** Not "everything I know about Ada." One thing
that happened.

**3. An inference needs a count.** If you write `inferred`, the `because`
should say how many times you have seen it:

```
inferred dislikes being interrupted
    when      mid-sentence, with other people in the room
    because   stopped talking and never picked it back up — three times
    on        2026-10-15
```

Once is a guess, not an inference. The checker warns you when the sample is
one or two, and it is right to.

**4. Never delete. Revise.**

```
    inferred dislikes surprises
        when      plans change without warning
        because   went quiet — three times
        on        2026-05-02
        revised   2026-05-09  "the quiet was about the flight"
```

Revising is not admitting a mistake. The revision *is* the data — it is the
only thing that makes the calibration line true. Deleting destroys exactly
what you came for.

**And one that is not a rule so much as a condition:** only write what you
would be willing to have read aloud. If you are softening it in case it is
seen, it stops being useful, and a softened record is worse than no record
because you will trust it.

---

## The first session

Do this once, today, in about ten minutes.

```sh
cd /Users/maaroofabdulkareem/Documents/deepseek-harness/default-workspace/portrait
python3 portrait.py add Ada
```

Pick one person who matters to you. Add **three to five things you currently
believe about them**, and answer `2) I worked it out` every time.

They are all inferences, because you have not been recording observations.
That is the point. This is the snapshot you will measure yourself against.

Give each one a room, a basis, and today's date. Then stop.

```
inferred generous
    when      when someone else is short
    because   covered the bill and never mentioned it — three times
    on        2026-10-15
```

Then close it and go and live. The file is now a baseline, and the baseline
is worthless today and valuable in a year.

---

## How it dies

Every personal record system fails the same four ways. Naming them is most of
the defence.

**It becomes a diary.** You record ordinary, expected behaviour, the file
fills with noise, and rereading it tells you nothing. The trigger is
*noticed* — not *happened*.

**It becomes your biases, written down.** You record conclusions without
observations, so the file is just what you already thought, with dates
attached, which now feels like evidence. Rule 1 is the fix.

**You never revise.** Nothing is ever marked wrong, so the calibration line
stays at zero and the tool gives you nothing you could not have guessed.

**You stop.** Usually in week three, because the payoff is a year away.

The fourth one is the real one, and it is why the recommendation is **two or
three people, not twenty**. The value here is longitudinal, not
cross-sectional. Twenty people for a month gives you nothing. Three people
for a year gives you the only sentence in this whole project you cannot get
any other way.

---

## The whole thing in six lines

```
When someone surprises you, or you catch yourself concluding:
    python3 portrait.py add <name>
    one claim — what a camera saw, where, and today's date.

When something changes your mind:
    python3 portrait.py revise <name>
    never edit the claim. Add a revision under it.

Before you act on your read of someone:
    python3 portrait.py report <name>
    is it observed or inferred, and how old?

Monthly:
    python3 portrait.py list
    which inferences are untested, which did you revise, and do the
    dates cluster?
```
