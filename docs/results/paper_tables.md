# HARP-PAF Publication Tables for IEEE Access Revision

## Table I: System Modules and Functional Architecture

| Module | File | Core Functions / Classes | Operational Role |
| :--- | :--- | :--- | :--- |
| Dynamic Scheduler | `backend/scheduler.py` | `HarpPolicy`, `run_dynamic` | Online user-space SMT dispatcher with non-preemptive queue management |
| Slowdown Regression | `backend/model.py` | `pair_duration`, `slowdown_risk`, `fit` | NNLS calibration model, analytical duration derivation, risk cost $J(i, j)$ |
| Adaptive Fusion | `backend/fusion.py` | `fuse`, `_perf_estimates`, `_probe_estimates` | Confidence-weighted blending of static instruction mix and runtime counter telemetry |
| Pair Features | `backend/features.py` | `sa_features`, `pair_vector`, `remaining` | Dominant bottleneck $H(i, j)$ calculation and dynamic phase progress alignment |
| Static Feature Extractor | `backend/static_features.py` | `analyze_binary`, `_loop_depths` | objdump disassembly analysis, instruction categorization, loop nesting recovery |
| Comparative Harness | `backend/benchmarks.py` | `evaluate`, `run_pairs`, `run_linux` | Pinned multi-repetition benchmark suite with shuffled order and SHA-256 checks |
| Baseline Policies | `backend/baselines.py` | `port_matching`, `random_matching` | Saito & Fujimoto PORT min-max heuristic, uniform random matching, OS default |

## Table II: System Parameter Setup and Experimental Constants

| Parameter | Symbol | Value | Unit | Definition & Design Rationale |
| :--- | :---: | :---: | :---: | :--- |
| Max Dynamic Confidence | $Q_{\max}$ | 0.90 | — | Caps dynamic telemetry weight to retain 10% static compiler prior even under stable runs |
| Window Stability Reference | $\sigma_{\text{ref}}$ | 0.25 | — | Reference within-phase standard deviation threshold for counter variance |
| Phase Support Threshold | $n_{\min}$ | 2 | windows | Minimum 100 ms counter windows required for full statistical confidence |
| Tail Penalty Multiplier | $\mu$ | 1.0 | — | Regularization weight penalizing single-thread worst-case slowdown exceeding tolerance $\tau$ |
| Model Uncertainty Weight | $\nu$ | 0.5 | — | Scales penalty with held-out RMSE when relying predominantly on uncalibrated static fallbacks |
| Tail Slowdown Tolerance | $\tau$ | 0.20 | — | Microarchitectural threshold permitting up to 20% slowdown before incurring tail penalty |
| Static Loop Weight | $W_{\text{loop}}$ | 10.0 | multiplier | Exponential frequency scaling factor applied per disassembly backward-branch nesting level |
| Sensitivity Cap | $S_{\max}$ | 2.0 | fraction | Maximum fractional execution time inflation under stressor probe (caps at 200%) |
| Aggressiveness Cap | $A_{\max}$ | 1.5 | ratio | Maximum normalized resource consumption relative to stressor signature |

## Table III: Evaluation Workload Suite Specifications (8 Synthetic Workloads)

| Workload ID | Source File | Microarchitectural Resource Stressed | Solo Runtime (s) | Dominant Instruction Mix | SHA-256 Output Checksum |
| :---: | :--- | :--- | :---: | :--- | :--- |
| T01 | `w1_integer_hash.cpp` | Xorshift hashing; integer ALU and multiplier bound | 0.681 | int_alu: 84.1%, branch: 7.2% | `HASH=17468124306509315085` |
| T02 | `w2_integer_divide.cpp` | Dependent 64-bit division and modulo; divider bound | 0.578 | int_alu: 74.0%, branch: 11.8% | `DIV=427229574` |
| T03 | `w3_fp_sqrt_chain.cpp` | Dependent square-root and divide chain; scalar FP bound | 0.717 | fp_simd: 40.7%, int_alu: 23.3% | `FP=2658312` |
| T04 | `w4_simd_saxpy.cpp` | Vectorised single-precision update on L1-resident arrays | 0.595 | fp_simd: 49.4%, load_store: 25.3% | `SIMD=835704` |
| T05 | `w5_memory_stream.cpp` | Sequential read-modify-write over 64 MiB | 0.740 | int_alu: 56.1%, load_store: 28.3% | `STREAM=1917314896346873856` |
| T06 | `w6_pointer_chase.cpp` | Dependent random loads through a 32 MiB cycle | 0.624 | int_alu: 45.5%, load_store: 25.9% | `CHASE=29366435976900` |
| T07 | `w7_branch_heavy.cpp` | Data-dependent unpredictable branches | 0.609 | int_alu: 67.1%, branch: 17.6% | `BRANCH=907649211104368865` |
| T08 | `w8_phased_mix.cpp` | Integer phase, then streaming phase, then branch phase | 0.901 | int_alu: 61.8%, branch: 16.7% | `PHASED=11593706697453564598` |

## Table IV: Microarchitectural Stressor and Calibration Kernels (10 Stressors)

| Kernel Name | Target Microarchitectural Subsystem | Stress Signature (gk) | Work Units | Role in Framework |
| :--- | :--- | :---: | :---: | :--- |
| `int` | Integer ALU pipeline saturation | 0.416 | 390 | Calibration & sensitivity probe |
| `div` | High-latency 64-bit integer divide port contention | 1.000 | 560 | Calibration & sensitivity probe |
| `fp` | Scalar floating-point divide & square-root saturation | 0.160 | 260 | Calibration & sensitivity probe |
| `simd` | Vectorized SIMD execution port pressure | 1.000 | 1600 | Calibration & sensitivity probe |
| `stream` | Main-memory bus bandwidth saturation (64 MiB stream) | 0.573 | 115 | Calibration & sensitivity probe |
| `chase` | LLC latency thrashing via random pointer chasing | 1.000 | 8 | Calibration & sensitivity probe |
| `cache` | L2/L3 cache capacity thrashing | 0.915 | 360 | Calibration & sensitivity probe |
| `branch` | Branch predictor capacity saturation & mispredictions | 0.751 | 150 | Calibration & sensitivity probe |
| `l1` | L1 data cache port bandwidth saturation | 1.000 | 900 | Calibration & sensitivity probe |
| `phased` | Multi-phase kernel transitioning between ALU and memory | 1.000 | 2 | Calibration & sensitivity probe |

## Table V: Comparative Experimental Results Across 10 Repetitions (Single Core SMT)

| Scheduling Method | Median Makespan (s) [95% CI] | Runtime Red. vs Base (%) | Speedup vs Base [95% CI] | ANTT | STP | Throughput (w/s) | Runs Faster |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **HARP-PAF (Dynamic)** | **3.202** [3.116, 3.400] | — | 1.000x [1.000, 1.000] | **1.12** | **7.25** | **2.50** | — |
| Random Dispatch | 3.495 [3.453, 3.651] | 8.4% | 1.091x [1.025, 1.159] | 1.21 | 6.77 | 2.29 | 10/10 |
| OS-Default (Windows 11) | 3.530 [3.433, 3.646] | 9.3% | 1.102x [1.020, 1.156] | 4.32 | 1.93 | 2.27 | 9/10 |
| HARP-PAF (Static Pairs) | 3.563 [3.526, 3.649] | 10.1% | 1.113x [1.043, 1.160] | 1.18 | 6.99 | 2.25 | 10/10 |
| PORT (Saito & Fujimoto) | 3.741 [3.583, 3.802] | 14.4% | 1.168x [1.075, 1.206] | 1.20 | 7.06 | 2.14 | 10/10 |
| Serial Execution (No SMT) | 5.465 [5.425, 5.684] | 41.4% | 1.707x [1.606, 1.795] | 1.00 | 8.00 | 1.46 | 10/10 |

## Table VI: Slowdown Prediction Accuracy and Held-Out Validation Comparison

| Metric / Dimension | Sensitivity x Aggressiveness (SA) Model | Primitive Feature-Equation Model | Difference / Improvement |
| :--- | :---: | :---: | :---: |
| Training MAE (55 calibration pairs) | **0.066** | 0.109 | 39.0% error reduction |
| Held-Out LOWO MAE (100 evaluations) | **0.069** | 0.129 | **46.2% error reduction** |
| Held-Out LOWO RMSE | **0.100** | 0.178 | 43.6% error reduction |
| Spearman Rank Correlation | **0.84** | 0.33 | **+154.5% rank alignment** |
| Evaluation Workload Pairs MAE | **0.060** | 0.114 | 47.4% error reduction |
| Pair Duration MAPE (%) | **9.03%** | 18.45% | Validates Eq. D(i, j) derivation |
| Evaluation Pairs Rank Correlation | **1.00** | 0.40 | Perfect pairing ordering |

## Table VII: Systematic Ablation Study: Isolating Adaptive Fusion and Phase Awareness

| System Configuration / Ablation Variant | Makespan (s) | Overhead vs HARP-PAF (%) | Initial Co-Runner next to T08 | Microarchitectural Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **HARP-PAF (Adaptive Fusion + Phase-Aware)** | **3.111** | **0.0%** | **T01** | Correctly pairs multi-phase workload with complementary ALU hash; tracks phase shifts |
| **Ablation 1: Static-Only ($q = 0$)** | 3.432 | +10.3% | T02 | Blind to dynamic memory/cache strides; pairs T08 with divide and T05 with T03 |
| **Ablation 2: Dynamic-Only ($q = 1$)** | 3.274 | +5.2% | T03 | Overfits to noisy counter samples on unstable probes (T03); ignores compile-time prior |
| **Ablation 3: Whole-Program Profile (No Phases)** | 3.266 | +5.0% | T07 | Averages out phase transitions in T08; causes collision during branch-heavy phase |

