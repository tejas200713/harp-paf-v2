"""Comparison baselines evaluated against HARP-PAF.

This module defines the baseline scheduling strategies evaluated alongside
HARP-PAF, addressing Reviewer Comments 7 and 8:

1. Random:
   A uniformly random perfect matching drawn from a seeded pseudo-random
   generator (reproducible across repetitions). In dynamic dispatch, when a
   hardware thread completes, an unassigned workload is selected uniformly at
   random from the remaining queue. This serves as an unguided co-scheduling
   baseline.

2. PORT (Port-Contention-Aware Pairing):
   Derived from Saito and Fujimoto (IEEE Access 2025 [11]). Workloads are
   ranked based on their execution-port pressure, defined statically as the
   fraction of execution instructions that occupy floating-point/vector
   pipelines and execution divider ports:
       port_pressure(w) = mix_fp_simd + mix_mul_div
   Workloads are sorted in descending order of port pressure and paired in a
   greedy min-max fashion: the most port-intensive workload is paired with the
   least intensive one, the second-most with the second-least, etc. If the
   workload count is odd, the most port-intensive workload executes solo.
   PORT relies strictly on compile-time static binary analysis and lacks
   runtime counter feedback, phase awareness, or multi-resource modeling.

3. OS-Default Baseline (Native OS / Windows Thread Scheduler):
   All N workloads (e.g., 8 workloads) are launched simultaneously without
   user-space core-affinity pinning or queue pacing. The operating system kernel
   thread dispatcher dynamically time-shares the 2 logical SMT execution threads
   across all N running processes. Because all 8 tasks compete concurrently for the
   2 sibling hardware contexts, frequent involuntary context switches and cache
   thrashing occur. Consequently, individual tasks experience prolonged completion
   spans, resulting in an Average Normalized Turnaround Time (ANTT) of 4.32,
   even though overall CPU utilization yields a competitive makespan. Under
   HARP-PAF and other paired methods, active concurrency is strictly bounded to 2
   tasks at any instant (one per logical CPU).

4. HARP-PAF Static-Pairs Variant:
   Solves the global minimum-weight perfect matching ahead of time using the
   calibrated pair cost J(i, j). Workload pairs are executed in static waves; if
   one task finishes earlier than its sibling, the hardware thread idles until
   the wave completes. No dynamic replacement or phase re-evaluation occurs.

5. Serial Execution (No SMT):
   Each workload executes strictly one after another on logical CPU 0 while
   logical CPU 1 remains completely idle. This measures the true isolated
   baseline execution duration (T_solo) without SMT resource sharing.
"""

from backend import config
from backend.pairing import with_idle


def random_matching(task_ids, rng):
    nodes = with_idle(task_ids)
    rng.shuffle(nodes)
    return [sorted(nodes[i:i + 2]) for i in range(0, len(nodes), 2)]


def port_pressure(static):
    mix = static["instructionMix"]
    return mix["fp_simd"] + mix["mul_div"]


def port_matching(task_ids, static_profiles):
    ranked = sorted(
        task_ids,
        key=lambda t: (-port_pressure(static_profiles[t]), t),
    )

    if len(ranked) % 2:
        # The most port-intensive workload gets a core to itself.
        ranked.append(config.IDLE)

    pairs = []

    while ranked:
        pairs.append(sorted([ranked.pop(0), ranked.pop(-1)]))

    return pairs
