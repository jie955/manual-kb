# English CS Retrieval Baseline · Task 1

**Generated**: 2026-07-08T06:35:46Z
**Model**: `_scratch/modelscope/BAAI/bge-m3` · **Queries**: 176

## Summary

| Slice | N | Scorable | Top1 | Top3 | MRR | Routing acc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| all | 176 | 109 | 0.6881 | 0.8349 | 0.7586 | 89.0% |
| tier_a_verbatim | 24 | 14 | 1.0 | 1.0 | 1.0 | 100.0% |
| corpus_direct | 64 | 64 | 0.7031 | 0.875 | 0.7792 | 85.9% |
| corpus_logic | 45 | 45 | 0.6667 | 0.7778 | 0.7293 | 93.3% |
| corpus_out | 67 | 0 | — | — | — | — |
| gate_direct_logic_tier_a | 14 | 14 | 1.0 | 1.0 | 1.0 | 100.0% |

## Routing method (all queries)

- **fan_out**: 61
- **keyword**: 115

## Top1 misses (scorable) · 34

- `csq_009` · logic · exp `['qa_001', 'qa_033']` → got `qa_035` (a3s/keyword) · `ET24 lock unlocks but gate opener won't move`
- `csq_011` · logic · exp `['qa_001', 'qa_033']` → got `qa_043` (a3s/keyword) · `UPS01 LOAD voltage drop ET24 electric lock`
- `csq_017` · logic · exp `['qa_001', 'qa_010']` → got `qa_025` (ad5s/keyword) · `AD8 DIP switch 5 photocell disconnect accessories`
- `csq_018` · logic · exp `['qa_001', 'qa_010']` → got `qa_015` (ad5s/fan_out) · `dual arm clutch release gate middle position won't open`
- `csq_053` · direct · exp `['qa_001', 'qa_002']` → got `qa_016` (ad5s/fan_out) · `gate erratically opening closing when push button wired to 4 and 5 witho…`
- `csq_054` · direct · exp `['qa_001', 'qa_002']` → got `qa_016` (ad5s/fan_out) · `disconnect 4 5 works remote reconnect cables without switch gate keeps c…`
- `csq_057` · direct · exp `['qa_001', 'qa_002']` → got `qa_011` (a3s/fan_out) · `third party push button dry contact must not have indicator circuits`
- `csq_072` · logic · exp `['qa_020', 'qa_021']` → got `qa_019` (a3s/keyword) · `AT12131 gate opens too far into grass limit switch B does nothing`
- `csq_073` · logic · exp `['qa_020', 'qa_021']` → got `qa_019` (a3s/keyword) · `adjusting screw B sliding limit switch gate still overswings`
- `csq_077` · logic · exp `['qa_020', 'qa_021']` → got `qa_022` (a3s/keyword) · `FORCE potentiometer SOFT STOP gate not closing fully`
- `csq_081` · direct · exp `['qa_022']` → got `qa_034` (a3s/keyword) · `detect voltage 11 12 terminals above 22V gate stops opening`
- `csq_095` · direct · exp `['qa_015', 'qa_016', 'qa_040']` → got `qa_022` (a3s/fan_out) · `power off before moving FORCE potentiometer auto close delay`
- `csq_101` · logic · exp `['qa_001']` → got `qa_015` (ad5s/keyword) · `dual swing disconnect one arm test which arm defective`
- `csq_110` · direct · exp `['qa_001', 'qa_002']` → got `qa_014` (a3s/keyword) · `A5 A8 gate opener batteries and AC adapter nothing works`
- `csq_111` · direct · exp `['qa_001', 'qa_002']` → got `qa_004` (a3s/keyword) · `not getting anything to work gate opener battery AC adapter installed`
- `csq_112` · direct · exp `['qa_001', 'qa_002']` → got `qa_027` (ad5s/fan_out) · `battery voltage more than 22VDC 11 12 terminals control board`
- `csq_114` · direct · exp `['qa_001', 'qa_002']` → got `qa_040` (ad5s/fan_out) · `DIP switch 3 OFF erase reprogram instant short 4 5 A5 gate opener`
- `csq_115` · direct · exp `['qa_001', 'qa_002']` → got `qa_033` (a3s/fan_out) · `ULT COM DLT limit switch faulty motor DC 24V test`
- `csq_118` · direct · exp `['qa_016', 'qa_020']` → got `qa_025` (ad5s/keyword) · `first open hard turned down stall force almost nothing AD5S`
- `csq_119` · direct · exp `['qa_016', 'qa_020']` → got `qa_005` (ad5s/keyword) · `remote not picking up cannot program learn control board AD5S`
- `csq_120` · direct · exp `['qa_016', 'qa_020']` → got `qa_037` (ad5s/keyword) · `pull to open gate bracket moving rod retracted open position too far`
- `csq_121` · direct · exp `['qa_016', 'qa_020']` → got `qa_015` (ad5s/keyword) · `gate bent from pressure force at bracket hydroelectric arm AD5S`
- `csq_122` · direct · exp `['qa_016', 'qa_020']` → got `qa_015` (ad5s/keyword) · `clear remote codes reprogram M12 AD5S dual swing`
- `csq_131` · logic · exp `['qa_001']` → got `qa_033` (a3s/keyword) · `A8132 dual swing lights blink click noise arms won't open or close`
- `csq_133` · logic · exp `['qa_001']` → got `qa_014` (a3s/keyword) · `motherboard receives signal from fob but arms won't move A8132`
- `csq_135` · logic · exp `['qa_001']` → got `qa_033` (a3s/keyword) · `disconnect accessories disable photocell erase reprogram A8132`
- `csq_136` · logic · exp `['qa_001']` → got `qa_015` (ad5s/keyword) · `release clutch push gate halfway dual swing won't move`
- `csq_147` · direct · exp `['qa_015', 'qa_016', 'qa_020']` → got `qa_040` (ad5s/keyword) · `AD5S left gate stopped before open position then closed itself no remote`
- `csq_148` · direct · exp `['qa_015', 'qa_016', 'qa_020']` → got `qa_019` (ad5s/keyword) · `dual swing gate reopened quarter way tried to close again multiple times`
- `csq_149` · direct · exp `['qa_015', 'qa_016', 'qa_020']` → got `qa_025` (ad5s/keyword) · `auto close set to max only stays open 2 seconds AD5S`
- `csq_170` · direct · exp `['qa_001', 'qa_033']` → got `qa_015` (ad5s/fan_out) · `neighbor Topens swing gate model A3 A5 A8 troubleshooting`
- `csq_173` · logic · exp `['qa_010']` → got `qa_016` (ad5s/fan_out) · `gate opens on second or third try sometimes first try remote`
- `csq_174` · logic · exp `['qa_010']` → got `qa_033` (a3s/keyword) · `control board clicks but gate doesn't move intermittent`
- `csq_176` · logic · exp `['qa_010']` → got `qa_011` (a3s/keyword) · `Topens gate opener remote intermittent click no movement no model`
