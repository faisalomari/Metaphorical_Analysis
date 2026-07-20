# Enhancement Plan

Prioritized recommendations to improve both the utility and the results of the thesis, based on
the full inventory in [THESIS_KNOWLEDGE.md](THESIS_KNOWLEDGE.md). Scope: the four-element framework
(kenning, trope, antonymy, simile), per the confirmed current thesis scope.

---

## 1. Per-element analysis

| Element | Status | Best result | Weakest point |
|---|---|---|---|
| **Simile (تشبيه)** | Strongest | 87.3% accuracy (gpt-5.2-pro zero-shot); 95.7% on the original explicit binary task (AraBERT) | Only tested on n=55-218; the *implicit*-simile case (the thesis's original proposal focus) is still only a 10-verse pilot |
| **Trope (مجاز)** | Second most developed | 67.5% accuracy (TabPFN + embeddings) | **LLMs underperform the embedding classifier** (GPT-5.2 zero/few-shot tops out at ~58%, worse than TabPFN's 67.5%) — unusual and worth investigating directly |
| **Kenning (كناية)** | Weak | None (TabPFN stalled, no LLM experiment) | Zero recoverable quantitative results anywhere in the repo |
| **Antonymy (طباق)** | Weakest | None (embedding pipeline never ran — path bug; TabPFN stalled) | Zero recoverable results, no LLM experiment at all, **and** the one dataset that exists has label leakage (several "negative" rows are themselves tagged طباق) |

**Concrete fixes per element:**
- **Antonymy**: fix the copy-paste bug in `experiments/classifiers/antonymy/FullEmbedding/embeddings.py` (still hardcodes Tashbeeh's filenames — never ran); fix the negative-set label leakage; add a first GPT zero-shot notebook mirroring `experiments/classifiers/simile/api/`.
- **Kenning**: same TabPFN-stall investigation as antonymy (likely a shared dependency/memory issue given the identical stall pattern across 3 of 4 elements); add GPT zero/few-shot experiments.
- **Trope**: run a focused error analysis on *why* LLMs underperform embeddings here specifically — trope/metaphor may require more world-knowledge grounding than pattern-matching, which cuts against the thesis's "LLMs vs. hard rhetorical elements" framing in an interesting way worth a dedicated discussion section.
- **Simile**: extend the existing 10-verse implicit-simile pilot (`writing/pilots/implicit simile - gpt5.pptx`) into a real dataset, since this was the original proposal's core contribution and directly tests the "challenging" angle of the thesis title.

---

## 2. Experimental improvements

1. **Build the missing evaluation harness** (highest leverage item in the whole project). Nothing in the repo currently scores any LLM or classifier output against the rich human ground truth that already exists (`data/ground_truth/ali_ana/`, `data/raw/haifa_corpus/all.csv`) for the *same poems*. This applies directly to the multi-model voting pipeline (already run on Imru' al-Qais Poem 8, for which ground truth exists) and to Forth_Step's JSONL outputs.
2. **Standardize test-set sizes across elements** — currently ranging from n=50 to n=1,594 across different Trope experiments alone, making cross-element and cross-model comparisons unreliable.
3. **Add statistical significance testing** (bootstrap confidence intervals or McNemar's test) — several reported accuracy differences (e.g. 0.575 vs. 0.581 for Trope zero-shot vs. few-shot) are well within noise at these sample sizes and shouldn't be reported as if meaningful without a test.
4. **Scale the multi-model voting pipeline beyond one poem.** It's the most architecturally mature code in the repo (retries, structured logging, crash-safe incremental writes) but has only ever processed 23 verses. Running it against the full 2,616-verse corpus, with the evaluation harness from (1) wired in, would give the first real cross-model, cross-element comparison with ground truth.
5. **Fix the broken Qwen integration** in the voting pipeline (bad API key, silently dropped) or remove it from `SUPPORTED_MODELS` if not worth fixing.
6. **Inter-annotator agreement**: ground truth throughout the project comes from a single annotator (Prof. Ali Hussein). SecondStep and ThirdStep's independent manual re-annotations of overlapping poems could serve as a natural double-annotation check — worth computing agreement (Cohen's kappa) between them before citing either as unambiguous ground truth.

---

## 3. Data improvements

1. **Fix Tebaq's negative-set label leakage** (5/387 and 6/188 "negative" rows are themselves tagged طباق).
2. **Fix FirstStep's duplicate-leakage risk**: diacritic stripping raised duplicate verse count from 86 to 3,696 in the exact file used for the train/test split; duplicates were never removed before splitting, inflating the reported 95.7% test accuracy to an unknown degree.
3. **Deduplicate the ~4-6 byte-identical copies** of the Trope and Simile datasets scattered across experiment subfolders — harmless today but a maintenance hazard if one copy is edited and others aren't.
4. **Balance dataset sizes across elements**: Kenning has ~2x more labeled examples than Trope/Simile/Antonymy, which may bias any cross-element comparison of model performance.
5. **Extend implicit-element augmentation to all four elements**, not just simile — directly serves the "challenging rhetorical elements" framing, since implicit/hidden instances are plausibly the harder cases the thesis title refers to.

---

## 4. Reproducibility

1. **Finish the `.env` migration** started in this reorg — every experiment script currently reads a local `key.txt`; point them at `os.environ` reading from `.env` instead (a small, mechanical change per script).
2. **Log the `LR.py` classifier×PCA-dimension sweep to disk.** Every element's 3-classifier × 6-dimension sweep (18 experiments per element, 72 total) is currently only printed to an uncaptured terminal — a two-line change (`summary_df.to_csv(...)`) recovers all of this.
3. **Debug and re-run the stalled TabPFN cells** (Kenning, Simile, Antonymy) — likely one shared root cause given the identical failure pattern.
4. **Consolidate the three independent per-element/per-approach pipelines** (embeddings+classical ML, single-model GPT, multi-model voting) behind one shared config/CLI so future experiments don't reinvent data loading, prompt templates, and output formats three times over.
5. **Add a `requirements.txt`/`environment.yml`** to `experiments/classifiers/` and `experiments/llm_pipelines/gpt1_single_model/` (currently only `multi_model_voting/` has one).

---

## 5. Thesis-writing implications

- **Related Work chapter**: already well-supported — `literature/authored/` (the advisors' own papers) and `literature/related_work/` (Abdul-Raof, the Arabic metaphor NMT paper, the rhetorical-relations classifier) give a solid foundation; minimal new work needed here.
- **Methods chapter**: currently would have to describe three disconnected methodologies. Item 4 in §4 (a unified pipeline) would let this be written as one coherent methods section instead of three.
- **Results chapter**: cannot currently be written for Kenning or Antonymy — these need real experiments before any results chapter is possible (see §1).
- **Discussion/Error Analysis chapter**: the Trope LLM-underperforms-embeddings finding, and the TabPFN-beats-zero-shot-GPT pattern generally, are already interesting, citable findings — worth a dedicated section rather than treating them as noise.
- **Limitations section**: the label-leakage, duplicate-leakage, and single-annotator-ground-truth issues (§3) should be disclosed regardless of whether they're fixed, since they currently caveat the strongest reported number in the whole project (FirstStep's 95.7%).

---

## 6. Roadmap (ordered, with effort estimates)

### Quick wins (hours–days)
1. Fix the Tebaq/Kenning `embeddings.py` copy-paste path bug and re-run — *~1 hour*
2. Debug the shared TabPFN stall and re-run for Kenning/Simile/Antonymy — *~half day, likely a dependency/version fix*
3. Log `LR.py`'s sweep results to CSV (all 4 elements) — *~1 hour*
4. Fix Tebaq's negative-set label leakage and re-balance — *~1 hour*
5. Rotate the exposed OpenAI API key (already flagged separately) — *~10 minutes, but time-sensitive*

### Medium effort (days–2 weeks)
6. Build the ground-truth evaluation harness joining `data/ground_truth/ali_ana` / `data/raw/haifa_corpus/all.csv` against classifier and LLM outputs — *~3-5 days; highest leverage item on this list*
7. Add GPT zero-shot + few-shot experiments for Kenning and Antonymy, mirroring Simile's `api/` folder — *~2-3 days*
8. Fix or drop Qwen in the voting pipeline; run it against the full 2,616-verse corpus with the harness from (6) wired in — *~1 week*
9. Add statistical significance testing to existing and new results — *~2 days*

### Bigger efforts (weeks+)
10. Extend implicit-element data augmentation from simile to all four elements — *~2-3 weeks, directly strengthens the thesis's core "challenging elements" claim*
11. Second-annotator / inter-annotator agreement study — *~1-2 weeks, depends on advisor/annotator availability*
12. Consolidate all three methodological lines into unified comparison tables and a single results chapter draft — *~1 week, once (6) and (8) are done*
