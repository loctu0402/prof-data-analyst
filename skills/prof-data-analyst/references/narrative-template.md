# Narrative Template — SCQR + Key Terms + Impact Cards

> Stakeholder-facing reports follow a fixed 3-block narrative skeleton: SCQR opening, Key Terms block, Impact Cards. Body sections come after.

## Overview — Why this file exists

Rule 1 (Orientation Block) mandates SCQR. That is necessary but not sufficient. A report that opens with SCQR but then dumps raw findings still loses the reader at the second screen. The full skeleton — SCQR + Key Terms + Impact Cards — is what makes the opening do its job: orient → ground → preview → invite-deeper-read.

## Outline (story-flow check)

1. SCQR (Situation / Complication / Question / Resolution)
2. Key Terms block (3-6 terms, diacritics correct, plain language)
3. Impact Cards (3-4 cards, sentiment colored, one-line takeaway)
4. Worked example (TTT daily snapshot pattern)
5. Anti-patterns

A reader scanning headings should be able to predict each block's role.

---

## Block 1: SCQR opening

**Pattern:**
```
Tình hình (Situation): <1 sentence, factual ground-state>
Vấn đề (Complication): <1 sentence, what changed or what is wrong>
Câu hỏi (Question): <1 sentence, the question this report answers>
Kết luận (Resolution): <1 sentence, the headline answer + recommended action>
```

**Pass signal:** A stakeholder reads only the SCQR block and walks away with the right action.
**Fail signal:** Resolution refers to an analysis the reader has not seen yet ("we recommend X based on Section 4").

**Why (Operational):** The first 30 seconds of a report determines whether the reader continues. SCQR collapses the report into 4 lines optimized for that 30 seconds.

## Block 2: Key Terms

**Pattern:** A definition block, 3-6 terms maximum, plain language, full Vietnamese diacritics.

**When required:** ALWAYS for stakeholder-facing reports. Even terms that "everyone knows" may have product-specific definitions (e.g., "DAU" — by which definition? login event? screen view? non-bot?).

**Format:**
```
**Thuật ngữ chính (Key Terms)**

- **DAU**: Số người dùng có ít nhất một sự kiện active (login + screen view + transaction) trong ngày. Loại bỏ bot và internal account.
- **TTT**: Tài khoản Tích Trữ — sản phẩm gửi tiết kiệm trên app, lãi suất X% năm, kỳ hạn linh hoạt.
- **Cashout**: Sự kiện rút tiền ra khỏi TTT về MoMo wallet, không phải về bank.
```

**Pass signal:** A new reader who never saw this product can read the Key Terms and follow the body.
**Fail signal:** Term is defined with another undefined term ("DAU is daily MAU"). Or: terms are missing diacritics ("Tai khoan Tich Tru").

**Why (Empirical):** Stakeholder slack channels are full of "what does X mean in this report?" — every such question is a Key Terms gap.

## Block 3: Impact Cards

**Pattern:** 3-4 cards in a row (or stacked on mobile). Each card has:
- One metric value
- Two comparisons (dual-comparison mandate: DoD + 7d avg)
- One sentiment color (context-aware, see §Sentiment override below)
- One-line takeaway (verdict: "đang tốt" / "cần chú ý" / "đã giảm rõ")

**Format (HTML approximation):**
```
[ Card: GMV ]                  [ Card: AUM ]                 [ Card: Cashout ]
  120 tỷ                          5.2 nghìn tỷ                  3.5 tỷ
  ▲ DoD +5%                       ▼ DoD −2%                     ▲ DoD +12%
  ▲ vs 7d avg +8%                 ▲ vs 7d avg +1%               ▲ vs 7d avg +15%
  [pink, đang tốt]                [pink, đang tốt]              [red, cần chú ý]
  Tuần này tăng đều               Hôm nay giảm nhẹ              Cashout cao hơn nền
                                  nhưng nền vẫn tăng            cần check tier
```

**Sentiment color override (CRITICAL):**
- Default: green / pink = positive, red = negative, gray = neutral.
- BUT: context flips the default. Example — "cashout↑" is RED in AUM-growth context (cashout reduces AUM) but may be GREEN in fintech-health context (proves liquidity). Document the override mapping in the report itself OR in a project config.

**Why (Empirical):** A single delta ("GMV +5%") is noise without comparison. The dual-comparison mandate (DoD + 7d avg) lets the reader distinguish trend from seasonality at a glance. Color delivers verdict in 100ms.

## Worked example: TTT daily snapshot opening

```
## Bối cảnh & Câu hỏi (SCQR)

Tình hình: Sản phẩm TTT đang chạy tháng thứ 4 của 2026, AUM 5.2 nghìn tỷ.
Vấn đề: Cashout đột biến tăng 12% ngày 2026-05-08 so với ngày trước, cao hơn 15% so với trung bình 7 ngày.
Câu hỏi: Đột biến cashout đến từ tier nào? Có cần can thiệp không?
Kết luận: Tier 3 (số dư <500k) chiếm 78% lượng cashout tăng thêm. Đề xuất kiểm tra notification campaign ngày 07/05 (tác động đến tier 3).

## Thuật ngữ chính (Key Terms)

- **TTT**: Tài khoản Tích Trữ — sổ tiết kiệm trên app.
- **AUM**: Tài sản đang quản lý — tổng số dư tất cả TTT chưa cashout.
- **Cashout**: Rút tiền từ TTT về wallet MoMo.
- **Tier**: Phân nhóm theo số dư — Tier 1 (>5M), Tier 2 (500k-5M), Tier 3 (<500k).

## Tóm tắt nhanh (Impact Cards)

[Tổng AUM]              [Cashout hôm nay]       [Tỷ lệ Cashout/AUM]    [Tier 3 share]
5.2 nghìn tỷ            3.5 tỷ                  0.067%                  78%
▼ DoD −0.2%              ▲ DoD +12%              ▲ DoD +12%              ▲ DoD +20pp
▲ vs 7d avg +1%          ▲ vs 7d avg +15%        ▲ vs 7d avg +14%        ▲ vs 7d avg +18pp
[pink, ổn định]          [red, đột biến]         [red, đột biến]         [red, dồn vào tier 3]
Nền tăng đều             Cao bất thường          Vượt ngưỡng 0.05%       Tier 3 dẫn dắt đợt
                         cần check tier          quan tâm                 cashout này
```

## Anti-patterns

- **SCQR with no Resolution.** The reader walks away unable to act.
- **Key Terms = a glossary at the END.** Reader hits an undefined term and bounces before reaching the glossary.
- **Impact Cards = a 10-column table.** Stakeholder eye-tracks 3-4 items, not 10.
- **Color used without context.** "Cashout ↑ = red" works for AUM-growth dashboard, fails for liquidity-monitoring dashboard. Document the override.
- **Single-delta KPI ("DoD +5%").** Without 7d avg, +5% on a Monday is meaningless — Mondays normally spike.
- **Diacritics dropped ("Tai khoan").** Stakeholder reads this as "AI-generated, low effort."

## Cross-references

- Rule 1 (Orientation Block) → `universal-workflow-rules.md`.
- Sentiment color override + chart anatomy + dual-comparison → `style-rules.md`.
- 5 Quality Criteria (this template feeds criteria 1, 4, 5) → `quality-criteria.md`.
- Outline / Story Flow Check applies to the rest of the body → `self-check-protocol.md` Section A2.

## Why this rule exists (Rule 4 meta)

SCQR alone primes the reader; Key Terms grounds the reader; Impact Cards previews the findings. Together they buy the analyst the next 5 minutes of attention. Skip any block and the report fights for attention instead of having it.
