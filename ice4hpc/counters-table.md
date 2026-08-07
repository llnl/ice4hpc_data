# Performance Counter Table across machines

Ideally we would collect all counters possible. This, however, isn't realistic, so we'll focus on the following counters/groups of counters:
* **branch** 
  * unconditional
  * conditional 
  * taken/non-taken
  * correctly-predicted/mispredicted
* **data and memory** 
  * load
  * store
  * LLC miss/hit
  * TLB miss/hit
  * page fault
  * i/d-L1 miss/hit
  * i/d-L2 miss/hit
* **arithmetic** 
  * integer
  * single precision
  * double precision
  * FMA (fused multiply and add or muladd)
* **vector** 
  * whatever SIMD
* **context switching**
* **IRQ or interrupts**
* **IO**

# Counters Already Collected
## AWS (C6i, C5i)
```
PAPI_BR_UCN
PAPI_BR_TKN
PAPI_BR_CN
PAPI_BR_INS
PAPI_BR_PRC
PAPI_L2_TCM
perf::DTLB-LOADS
perf::DTLB-LOAD-MISSES
perf::DTLB-STORES
perf::DTLB-STORE-MISSES
perf::ITLB-LOADS
perf::ITLB-LOAD-MISSES
perf::LLC-LOADS 
perf::LLC-LOAD-MISSES
perf::LLC-STORES
perf::LLC-STORE-MISSES
perf::L1-DCACHE-LOADS
perf::L1-DCACHE-LOAD-MISSES
perf::L1-DCACHE-STORES
perf::L1-DCACHE-STORE-MISSES
PAPI_SP_OPS
PAPI_DP_OPS
PAPI_VEC_SP
PAPI_VEC_DP
perf::PERF_COUNT_SW_CONTEXT_SWITCHES
perf::CONTEXT-SWITCHES
IO

Just on C5i:
clx::RESOURCE_STALLS
clx::HW_INTERRUPTS
```

## Mammoth
```
PAPI_BR_INS
perf::L1-DCACHE-LOADS
perf::LLC-LOADS
perf::L1-DCACHE-STORES
perf::LLC-STORES 
PAPI_TOT_INS
perf::L1-DCACHE-LOAD-MISSES
perf::LLC-STORE-MISSES
perf::LLC-LOAD-MISSES
PAPI_L2_DCM
PAPI_FP_OPS
amd64_fam17h_zen2::RETIRED_SSE_AVX_FLOPS
IO
REALTIME
```

# Counters Table

| Metric                                | AWS (Collected)                | Mammoth (Collected)                      | Poodle                      |
| :------------------------------------ | :----------------------------- | :--------------------------------------- | :-------------------------- |
| **Branches**                          |
| total branches/unconditional branches | PAPI_BR_UCN                    | PAPI_BR_INS                              | perf::BRANCH-INSTRUCTIONS   |
| conditional branches                  | PAPI_BR_CN                     | -                                        | -                           |
| branch taken                          | PAPI_BR_TKN                    | -                                        | -                           |
| branch mispredicted                   | PAPI_BR_PRC                    | -                                        | perf::BRANCH-MISSES         |
| **Data and Memory**                   |
| DTLB Loads                            | perf::DTLB-LOADS               | -                                        | perf::BRANCH-MISSES         |
| DTLB Load Misses                      | perf::DTLB-LOAD-MISSES         | -                                        | perf::DTLB-LOAD-MISSES      |
| DTLB Stores                           | perf::DTLB-STORES              | -                                        | perf::DTLB-STORES           |
| DTLB Store Misses                     | perf::DTLB-STORE-MISSES        | -                                        | perf::DTLB-STORE-MISSES     |
| L1 Loads                              | perf::L1-DCACHE-LOADS          | perf::L1-DCACHE-LOADS                    | perf::L1-DCACHE-LOADS       |
| L1 Load Misses                        | perf::L1-DCACHE-LOAD-MISSES    | perf::L1-DCACHE-LOAD-MISSES              | perf::L1-DCACHE-LOAD-MISSES |
| L1 Stores                             | perf::L1-DCACHE-STORES         | perf::L1-DCACHE-STORES                   | perf::L1-DCACHE-STORES      |
| L1 Store Misses                       | perf::L1-DCACHE-STORE-MISSES   | -                                        | -                           |
| L2 Loads                              | -                              | -                                        | -                           |
| L2 Load Misses                        | -                              | -                                        | -                           |
| L2 Stores                             | -                              | -                                        | -                           |
| L2 Store Misses                       | -                              | -                                        | -                           |
| L3 Loads                              | perf::LLC-LOADS                | perf::LLC-LOADS                          | perf::LLC-LOADS             |
| L3 Load Misses                        | perf::LLC-LOAD-MISSES          | perf::LLC-LOAD-MISSES                    | perf::LLC-LOAD-MISSES       |
| L3 Stores                             | perf::LLC-STORES               | perf::LLC-STORES                         | perf::LLC-STORES            |
| L3 Store Misses                       | perf::LLC-STORE-MISSES         | perf::LLC-STORE-MISSES                   | perf::LLC-STORE-MISSES      |
| Page Faults                           | -                              | -                                        | perf::PAGE-FAULTS           |
| Other                                 | PAPI_L2_TCM                    | PAPI_L2_DCM                              | -                           |
| **Arithmetic**                        |
| SP FP Operations                      | PAPI_SP_OPS                    | PAPI_FP_OPS                              | -                           |
| DP FP Operations                      | PAPI_DP_OPS                    | -                                        | -                           |
| **Vector**                            |
| SP Vector Instructions                | PAPI_VEC_SP                    | -                                        | -                           |
| DP Vector Instructions                | PAPI_VEC_DP                    | -                                        | -                           |
| **Context Switching**                 |
| Context Switches                      | perf::CONTEXT-SWITCHES         | -                                        | perf::CONTEXT-SWITCHES      |
| **IRQ**                               |
| Interrupts                            | -                              | -                                        | -                           |
| **IO**                                |
| IO                                    | IO                             | IO                                       | IO                          |
| **Time**                              |
| Execution Time                        | REALTIME                       | REALTIME                                 | REALTIME                    |
| **Instructions**                      |
| Total Instructions                    | -                              | PAPI_TOT_INS                             | perf::INSTRUCTIONS          |
| **Other**                             |
|                                       | clx::RESOURCE_STALLS (only C5) | amd64_fam17h_zen2::RETIRED_SSE_AVX_FLOPS |                             |
|                                       | clx::HW_INTERRUPTS (only C5)   |                                          |                             |
| **Notes**                             |                                | Limited PAPI support                     |                             |
