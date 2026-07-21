# English CS Retrieval Baseline · Task 1

**Generated**: 2026-07-08T14:54:02Z
**Model**: `_scratch/modelscope/BAAI/bge-m3` · **Queries**: 176

## Summary

| Slice | N | Scorable | Top1 | Top3 | MRR | Routing acc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| all | 176 | 109 | 0.578 | 0.6881 | 0.6284 | 88.1% |
| tier_a_verbatim | 24 | 14 | 1.0 | 1.0 | 1.0 | 92.9% |
| corpus_direct | 64 | 64 | 0.6406 | 0.7188 | 0.6771 | 87.5% |
| corpus_logic | 45 | 45 | 0.4889 | 0.6444 | 0.5593 | 88.9% |
| corpus_out | 67 | 0 | — | — | — | — |
| gate_direct_logic_tier_a | 14 | 14 | 1.0 | 1.0 | 1.0 | 92.9% |

## Routing method (all queries)

- **fan_out**: 59
- **keyword**: 117

## Top1 misses (scorable) · 46

- `csq_007` · logic · exp `['qa_001', 'qa_033']` → got `qa_037` (a3s/keyword) · `gate opener worked four days now motor won't function lock still unlocks`
- `csq_009` · logic · exp `['qa_001', 'qa_033']` → got `qa_037` (a3s/keyword) · `ET24 lock unlocks but gate opener won't move`
- `csq_010` · logic · exp `['qa_001', 'qa_033']` → got `qa_019` (a3s/fan_out) · `bypassed motor limit switch jumping wires still nothing`
- `csq_011` · logic · exp `['qa_001', 'qa_033']` → got `qa_034` (a3s/keyword) · `UPS01 LOAD voltage drop ET24 electric lock`
- `csq_012` · logic · exp `['qa_001', 'qa_033']` → got `qa_011` (a3s/fan_out) · `tested power at control board going to the motor zero power`
- `csq_016` · logic · exp `['qa_001', 'qa_010']` → got `qa_007` (a3s/fan_out) · `programmed remotes gate opener no movement LED blinks`
- `csq_017` · logic · exp `['qa_001', 'qa_010']` → got `qa_015` (ad5s/keyword) · `AD8 DIP switch 5 photocell disconnect accessories`
- `csq_018` · logic · exp `['qa_001', 'qa_010']` → got `qa_038` (a3s/fan_out) · `dual arm clutch release gate middle position won't open`
- `csq_048` · direct · exp `['qa_001', 'qa_002']` → got `qa_033` (a3s/keyword) · `immediately short push button terminals 4 5 control board video`
- `csq_053` · direct · exp `['qa_001', 'qa_002']` → got `qa_031` (ad5s/fan_out) · `gate erratically opening closing when push button wired to 4 and 5 witho…`
- `csq_054` · direct · exp `['qa_001', 'qa_002']` → got `qa_007` (a3s/fan_out) · `disconnect 4 5 works remote reconnect cables without switch gate keeps c…`
- `csq_057` · direct · exp `['qa_001', 'qa_002']` → got `qa_011` (a3s/fan_out) · `third party push button dry contact must not have indicator circuits`
- `csq_072` · logic · exp `['qa_020', 'qa_021']` → got `qa_019` (a3s/keyword) · `AT12131 gate opens too far into grass limit switch B does nothing`
- `csq_073` · logic · exp `['qa_020', 'qa_021']` → got `qa_019` (a3s/keyword) · `adjusting screw B sliding limit switch gate still overswings`
- `csq_074` · logic · exp `['qa_020', 'qa_021']` → got `qa_034` (a3s/keyword) · `gate closes very slow stops halfway AT12131`
- `csq_076` · logic · exp `['qa_020', 'qa_021']` → got `qa_019` (a3s/keyword) · `reconfirm open closed position pull to open limit switch B`
- `csq_077` · logic · exp `['qa_020', 'qa_021']` → got `qa_022` (a3s/keyword) · `FORCE potentiometer SOFT STOP gate not closing fully`
- `csq_081` · direct · exp `['qa_022']` → got `qa_034` (a3s/keyword) · `detect voltage 11 12 terminals above 22V gate stops opening`
- `csq_082` · direct · exp `['qa_022']` → got `qa_030` (a3s/keyword) · `FORCE potentiometer SOFT STOP gate not opening all the way`
- `csq_083` · direct · exp `['qa_022']` → got `qa_017` (ad5s/fan_out) · `push against gate during opening add load test gate opener`
- `csq_095` · direct · exp `['qa_015', 'qa_016', 'qa_040']` → got `qa_036` (ad5s/keyword) · `power off before moving FORCE potentiometer auto close delay`
- `csq_101` · logic · exp `['qa_001']` → got `qa_015` (ad5s/keyword) · `dual swing disconnect one arm test which arm defective`
- `csq_108` · logic · exp `['qa_033']` → got `qa_011` (a3s/keyword) · `DIP switch 3 OFF disconnect accessories A5131 troubleshooting`
- `csq_111` · direct · exp `['qa_001', 'qa_002']` → got `qa_014` (a3s/keyword) · `not getting anything to work gate opener battery AC adapter installed`
- `csq_114` · direct · exp `['qa_001', 'qa_002']` → got `qa_031` (ad5s/fan_out) · `DIP switch 3 OFF erase reprogram instant short 4 5 A5 gate opener`
- `csq_115` · direct · exp `['qa_001', 'qa_002']` → got `qa_033` (a3s/fan_out) · `ULT COM DLT limit switch faulty motor DC 24V test`
- `csq_117` · direct · exp `['qa_016', 'qa_020']` → got `qa_015` (ad5s/keyword) · `AD5S dual solar gate opens too far gets binded sometimes doesn't close`
- `csq_118` · direct · exp `['qa_016', 'qa_020']` → got `qa_040` (ad5s/keyword) · `first open hard turned down stall force almost nothing AD5S`
- `csq_119` · direct · exp `['qa_016', 'qa_020']` → got `qa_006` (ad5s/keyword) · `remote not picking up cannot program learn control board AD5S`
- `csq_120` · direct · exp `['qa_016', 'qa_020']` → got `qa_037` (ad5s/keyword) · `pull to open gate bracket moving rod retracted open position too far`
- `csq_121` · direct · exp `['qa_016', 'qa_020']` → got `qa_040` (ad5s/keyword) · `gate bent from pressure force at bracket hydroelectric arm AD5S`
- `csq_122` · direct · exp `['qa_016', 'qa_020']` → got `qa_015` (ad5s/keyword) · `clear remote codes reprogram M12 AD5S dual swing`
- `csq_131` · logic · exp `['qa_001']` → got `qa_033` (a3s/keyword) · `A8132 dual swing lights blink click noise arms won't open or close`
- `csq_132` · logic · exp `['qa_001']` → got `qa_033` (a3s/fan_out) · `control board has power will not send power to arm terminals`
- `csq_133` · logic · exp `['qa_001']` → got `qa_037` (a3s/keyword) · `motherboard receives signal from fob but arms won't move A8132`
- `csq_135` · logic · exp `['qa_001']` → got `qa_033` (a3s/keyword) · `disconnect accessories disable photocell erase reprogram A8132`
- `csq_136` · logic · exp `['qa_001']` → got `qa_041` (ad5s/keyword) · `release clutch push gate halfway dual swing won't move`
- `csq_146` · direct · exp `['qa_015', 'qa_016', 'qa_020']` → got `qa_040` (ad5s/keyword) · `I installed the AD5S gate opener on Saturday. Everything was working gre…`
- `csq_147` · direct · exp `['qa_015', 'qa_016', 'qa_020']` → got `qa_040` (ad5s/keyword) · `AD5S left gate stopped before open position then closed itself no remote`
- `csq_148` · direct · exp `['qa_015', 'qa_016', 'qa_020']` → got `qa_019` (ad5s/keyword) · `dual swing gate reopened quarter way tried to close again multiple times`
- … and 6 more (see JSON)
