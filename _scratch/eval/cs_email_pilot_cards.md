# Phase 0.2 · Pilot Cards

**Purpose**：结构化 Pilot case — E2E Grounding / Style 对照 Reference。  
**Plan**：[Implementation Plan §4.2](./cs_en_implementation_plan.md)  
**Date**：2026-07-07

---

## Pilot A · `cs_0001` · AT12131S gate no response

| Field | Value |
| --- | --- |
| **Source** | [`0001-at12131s-gate-no-response.md`](../../samples/customer-service-emails/0001-at12131s-gate-no-response.md) |
| **Customer query** | `AT12131S gate does nothing when I push the button` |
| **Routing** | `logic` → **`a3s` `qa_011`**（board-family；勿 blind `ad5s` `qa_010`） |
| **P0 grounding** | DIP **#3** OFF · 11#/12# >22V · instant short 4#/5# · motor direct 24V · limit short ULT/COM/DLT |
| **Reference agent** | Joyce 2026-06-15（四步梯 + fuse/LED in step 1） |

### Customer email (verbatim excerpt)

```text
Product Model: TOPENS AT12131S
Body: the gate does nothing when i push the button or use the key pad remote.
```

### Grounding checklist (Gate G)

| Step | Reference (Joyce) | Expected from `qa_011` EN |
| ---: | --- | --- |
| 1 | BAT 11#/12# >22V · fuse/LED | ✅ in `answer_en` |
| 2 | Disconnect accessories · DIP **#3** off · reprogram · short 4#/5# | ✅ DIP #3 |
| 3 | Motor direct 24V red/black | ✅ |
| 4 | Short ULT/COM/DLT · limit test | ✅ |

### E2E command (when API configured)

```powershell
python _scratch/eval/run_cs_side_by_side_gen.py
# or qa_server --unified-cs --demo-presentation cs-email
```

### Context smoke

[`phase0_pilot_context_smoke.md`](./phase0_pilot_context_smoke.md) · `python _scratch/eval/run_phase0_pilot_context.py`

---

## Pilot B · `cs_0008` · PW502 + TC148 push button

| Field | Value |
| --- | --- |
| **Source** | [`0008-pw502-tc148-push-button-not-working.md`](../../samples/customer-service-emails/0008-pw502-tc148-push-button-not-working.md) |
| **Customer query** | TC148 / 4# & 5# no response · jumper already tried |
| **Routing** | `direct` → **`tc148` `qa_002`** |
| **P0 grounding** | TC148 wiring · O.S.B/COM · shielded cable · control board terminals |
| **Reference agent** | Lori / Joyce thread |

### Customer email (verbatim excerpt)

```text
Push button not working, therefore we jumpered out #4&5 at the main control panel
and still nothing happened. Other than that everything works.
Product Model: PW502 · Accessories: TC148 waterproof push button
```

### Grounding checklist (Gate G)

| Item | Note |
| --- | --- |
| TC148 on 4#/5# (O.S.B/COM) | TC148 库 troubleshooting EN |
| Customer already jumpered 4&5 | Reply must **acknowledge** prior step |
| Template vs troubleshooting | `customer_reply_templates` **must not** pollute LLM context |

### Context smoke

Same script — `cs_0008` section in [`phase0_pilot_context_smoke.md`](./phase0_pilot_context_smoke.md)

---

## Phase 0.3 · Internal Review（待填）

**Plan**：[Implementation Plan §4.3](./cs_en_implementation_plan.md) · 殷主管 review **可选**（部署后）

| Pilot | G · Context-only (0.1) | S · Context-only | G · EN Index (1a) | S · EN Index | Reviewer | Date |
| --- | --- | --- | --- | --- | --- | --- |
| cs_0001 | 4 | 3 | | | Eng | 2026-07-07 |
| cs_0008 | 4 | 3 | | | Eng | 2026-07-07 |

> **双列说明**：0.2/0.3 填 **Context-only**（中文索引 + EN context）；Phase 1a 完成后补 **EN Index** 列，用于量化 EN 索引对 G/S 的增量。

主表同步：[`cs_client_feedback_pack.md`](./cs_client_feedback_pack.md)
