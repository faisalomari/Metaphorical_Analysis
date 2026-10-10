# Discussion (draft)

**Status**: draft, written 2026-07-26, in response to a supervisor meeting the same week.
Not yet reviewed. Terminology follows `GLOSSARY.md`'s 2026-07-23 corrections throughout (this
is new writing) — trope's constituent subtypes are named where relevant, antithesis
replaces antonymy, periphrasis replaces kenning. Phase 1 numbers are cited under their
corrected names with a parenthetical noting the frozen artifact's original term, per
`GLOSSARY.md`'s own citation convention.

## Refining the "simple vs. complex" hypothesis: marker explicitness, not intuitive difficulty

One reading of this thesis's results, and the one the supervisors' meeting note proposed as
a working hypothesis, is that the four rhetorical elements split along a simple-to-complex
axis, with models handling the simpler ones well and the more complex ones poorly. The
frozen evidence supports part of this — the four elements are not equally hard — but the
axis that actually separates them, once the per-subtype and per-element evidence is laid
side by side, is narrower and more mechanical than "simple vs. complex": **what predicts a
model's success is not how conceptually sophisticated a figure is, but whether its surface
form gives the model a locatable anchor that forecloses (or need not foreclose) the literal
reading, versus requiring the model to hold two readings in tension or recognize a closed
lexical class it may never have seen enumerated.** This is a sharpening of the supervisors'
hypothesis, not a rebuttal of it — the ordering it predicts is largely the same ordering the
frozen results already show — but it explains two things a pure "simple vs. complex" framing
cannot: why one of the intuitively hardest trope subtypes turned out to be the easiest, and
why the intuitively simplest element (antithesis, a bare lexical opposition) is not simply
"good" but fails in its own specific way.

**Simile is best because its explicit marker is also its complete definition.** Simile's own
definition names the comparative particle (كأنّ، كما، الكاف) as *the* defining feature, and
performance tracks this almost exactly: simile is the best-performing element under both the
baseline and the corrected prompt for every model, with strict-criterion F1 in the 0.65-0.73
range under the corrected prompt — roughly three to seven times higher than periphrasis's
best score on the same evaluation. <!-- source: PROJECT_STATE.md §3a; frozen Phase 1
"kenning"/simile TEST F1, cited under corrected terms --> There is little for the model to
infer beyond locating the particle and its two flanking terms; the task is close to
detection rather than interpretation.

**Antithesis is detectable but over-claimed — a distinct failure mode, not a milder version
of the same problem.** Antithesis's defining signal, a pair of lexically opposed terms in one
context, is in principle just as locatable as simile's particle, and the frozen evidence
shows models do find lexical opposition readily — the problem is that they find it too
readily. Under the corrected prompt, false positives exceed true positives for every model
(Claude Sonnet 4.6: 6 true positives against 12 false positives, strict criterion; GPT-5.4-mini
and Gemini 3.5 Flash show the same pattern), a pattern invisible on the two-poem development
set (whose antithesis support was a single instance on one poem) and only exposed once the
frozen test set's larger antithesis support (43 instances) made it measurable.
<!-- source: PROJECT_STATE.md §3a, §3d --> This is a precision failure sitting on top of
adequate recall, not a recall failure like periphrasis's — a model that over-generalizes "two
opposed words" into "antithesis" without also checking that the opposition is the point of
the line, rather than a model that cannot find the opposition at all. A hypothesis organized
only around "how hard is this element" would group antithesis with simile as an "easy"
element and miss this qualitatively different failure mode entirely.

**Trope's verb-anchored subtype (استعارة فعل) is hard but prompt-improvable, because a
semantically anomalous verb usage forecloses the literal reading almost as cleanly as an
explicit particle does.** استعارة فعل — a verb used in a sense whose literal reading would be
nonsensical in context — is trope's largest subtype by volume (76 of 179 test instances) and
the one the corrected prompt's added rules were built to address; it moved from 83% missed
under the baseline prompt to 62% missed under the corrected one, the largest subtype-level
gain the frozen evaluation recorded. <!-- source: PROJECT_STATE.md §3c --> The anomaly itself
is not hidden — a verb used where its literal sense cannot apply is a locatable
incongruity — but locating *which* verb and confirming the incongruity requires a small
inferential step a bare particle does not, which is consistent with this subtype improving
substantially with better instructions rather than starting near-ceiling like simile.

**The same mechanism explains an apparent exception the supervisors flagged as worth
investigating: whole-clause metaphor (استعارة تمثيلية) has no explicit marker at all, and was
initially hypothesized as the hardest trope subtype on the two-poem development set, yet
turned out to be the *easiest* subtype at test scale (33% missed under the baseline prompt,
29% under the corrected one — better than every other subtype with meaningful support).
<!-- source: PROJECT_STATE.md §3c --> This is not a counter-example to the marker-explicitness
account so much as a case that clarifies what "marker" should mean: whole-clause metaphor
lacks a lexical particle, but the figurative reading is typically the *only* sensible one for
the entire clause — there is no competing literal reading left standing, much as a
semantically anomalous verb forecloses the literal sense in استعارة فعل. The operative
variable, restated more precisely than "has an explicit marker," is whether *some* feature of
the line — a particle, a lexical opposition, or an anomaly that makes the literal reading
untenable — closes off the alternative reading for the model, or leaves it open.

**Periphrasis and lexicalized metonymy (مجاز مرسل) are hardest for exactly the reason their
own definitions predict: the literal reading is required to remain plausible, and no
locatable anomaly closes it off.** Periphrasis is, by definition, an indirect expression
whose literal sense stays available even as the intended sense is something else; there is no
foreclosure signal for the model to key on, which is consistent with periphrasis being the
hardest element under every configuration tried in this project — strict-criterion F1 never
exceeding 0.18 anywhere in the frozen evaluation, against simile's 0.65-0.73.
<!-- source: PROJECT_STATE.md §3a --> مجاز مرسل, similarly, stayed at 85% missed under both the
baseline and corrected prompts, identically — the one trope subtype no Phase 1 intervention
moved at all — because it is a closed, enumerable class of conventionalized substitutions
(the sky "raining" when the cloud is the actual agent; a name for wine when grapes are what
is literally pressed) rather than a compositional pattern inferable from a definition and a
few worked examples. <!-- source: PROJECT_STATE.md §3c; GLOSSARY.md -->

**Phase 2's evidence adds one further, important qualification: format change helps periphrasis
and مجاز مرسل, but only stochastically, not reliably.** Allowing the model free-form Arabic
reasoning before answering (rather than a closed-form, no-explanation JSON schema) produced
the largest periphrasis recall gain observed anywhere in this project — strict F1 0.111 to
0.316 on one development poem, catching a periphrasis instance every prior configuration in
this project had missed, with a substantively correct rhetorical justification.
<!-- source: report_3i.md §3, §5 --> But a second independent run of the same free-form
configuration frequently disagreed with the first about *which* phrase in the verse deserved
the tag: of the periphrasis and مجاز مرسل instances the free-form configuration could reach at
all, most were caught in only one of two independent runs, so the project's standard 2-run-majority
convention — appropriate everywhere else in this thesis — collapses most of that
apparent gain back down. <!-- source: report_3i.md §8, §9 --> This is consistent with, and
sharpens, the marker-explicitness account: where no locatable anomaly closes off the literal
reading, giving the model room to reason does let it *find* the intended reading some of the
time, but does not give it a stable criterion for deciding among competing readings the way an
explicit particle or a semantic anomaly does — the model can reach the right answer without
having a reliable way to recognize it as the right answer twice in a row.

**Net statement of the refined hypothesis**: the four elements are not ordered by an
intuitive notion of conceptual complexity, but by how much of the burden of resolving
figurative intent an explicit surface signal already carries versus how much is left to
inference over an unstated or closed-class relation. Simile's particle carries nearly all of
it; antithesis's lexical opposition carries the detection burden but not the "is this the
point of the line" judgment, producing over-claiming rather than under-detection; trope's
verb-anchored and whole-clause subtypes carry enough of it that better instructions recover
much of the gap; periphrasis and مجاز مرسل carry the least, and free-form reasoning — the one
intervention that moves them at all — trades a stable criterion for an occasional correct
guess.
