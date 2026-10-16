"""Poem-level splitting, stratified by poet where possible.

Algorithm: group poems by poet, shuffle poet order and each poet's own poems
(both seeded), then build one processing sequence that round-robins across
poets (take poet 1's next poem, poet 2's next poem, ... cycle) so a poet's
own poems are spread out in time rather than processed back-to-back. Walk
that sequence and assign each poem, one at a time, to the split with the
largest current deficit (target_ratio*n_assigned_so_far - split's running
count) -- the standard sequential/"highest-averages" apportionment method.

This hits the target global ratios almost exactly (apportionment methods are
guaranteed within ~1 unit of exact, unlike doing largest-remainder rounding
independently per poet-group, which badly under-fills minority splits when
most poet-groups are tiny -- verified during development: 70/15/15 with
per-group independent rounding starved `test` down to ~10% because every
2-poem poet's largest-remainder tie went to `train`). The round-robin
interleaving means that whenever a poet has enough poems, later ones are
assigned once other splits have grown a bigger deficit, so they tend to
land in a different split than the poet's earlier poems -- "stratified by
poet where possible," not a hard per-poet-in-every-split guarantee (not
possible for the poets with only 1-2 poems, the large majority here).

Every random draw is seeded deterministically from (seed, poet_name) so a
given seed always produces the same split, and changing the seed only
reshuffles.
"""
import hashlib
import random


def _poet_seed(seed: int, poet: str) -> int:
    h = hashlib.sha256(f"{seed}:{poet}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def _interleaved_order(poems: list, seed: int) -> list:
    """Round-robins across poets (each poet's own poems pre-shuffled)."""
    by_poet = {}
    for p in poems:
        by_poet.setdefault(p["poet_name"], []).append(p["poem_id"])
    poet_order = sorted(by_poet)  # stable base order before shuffling
    rng = random.Random(_poet_seed(seed, "__poet_order__"))
    rng.shuffle(poet_order)
    for poet in poet_order:
        rng2 = random.Random(_poet_seed(seed, poet))
        rng2.shuffle(by_poet[poet])

    sequence = []
    i = 0
    remaining = {poet: list(ids) for poet, ids in by_poet.items()}
    active = list(poet_order)
    while active:
        poet = active[i % len(active)]
        if remaining[poet]:
            sequence.append(remaining[poet].pop(0))
            i += 1
        else:
            active.remove(poet)
            if not active:
                break
            i = i % len(active)
    return sequence


def stratified_poet_split(poems: list, split_names: list, ratios: list, seed: int) -> dict:
    """poems: list of {"poem_id": str, "poet_name": str, ...}.
    Returns {split_name: [poem_id, ...]}, hitting `ratios` almost exactly via
    sequential apportionment over a poet-interleaved processing order."""
    assert len(split_names) == len(ratios)
    assert abs(sum(ratios) - 1.0) < 1e-6

    order = _interleaved_order(poems, seed)
    counts = {name: 0 for name in split_names}
    out = {name: [] for name in split_names}
    n_assigned = 0
    for poem_id in order:
        n_assigned += 1
        deficits = [ratios[i] * n_assigned - counts[split_names[i]] for i in range(len(split_names))]
        best = max(range(len(split_names)), key=lambda i: deficits[i])
        name = split_names[best]
        counts[name] += 1
        out[name].append(poem_id)
    return out


def carve_val_from_train(train_ids: list, poems_by_id: dict, val_frac: float, seed: int) -> dict:
    """Splits an existing train poem-id list into {"train":[...], "val":[...]}
    via the same poet-stratified mechanism, treating train_ids as the full pool."""
    sub_poems = [poems_by_id[pid] for pid in train_ids]
    return stratified_poet_split(sub_poems, ["train", "val"], [1 - val_frac, val_frac], seed)
