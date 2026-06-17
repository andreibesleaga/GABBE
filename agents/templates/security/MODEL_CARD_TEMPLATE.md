# Model Card: [MODEL_NAME]

<!-- Model Card in the Mitchell et al. style. Fill every [PLACEHOLDER]. -->
<!-- Store in: docs/security/model-cards/[model-name]-model-card.md -->
<!-- Keep this card versioned alongside the model; update on every retrain or eval change. -->

---

## 1. Model Details

| Field | Value |
|---|---|
| Model name | [MODEL_NAME] |
| Version | [VERSION] |
| Owner / team | [OWNER_TEAM] |
| Point of contact | [CONTACT] |
| Date released | [DATE] |
| Model type | [e.g. transformer LLM / fine-tune of BASE_MODEL / classifier / distilled SLM] |
| Base / parent model | [BASE_MODEL or "trained from scratch"] |
| Architecture summary | [ARCHITECTURE] |
| License | [LICENSE] |
| Citation / how to cite | [CITATION] |

---

## 2. Intended Use

### In-scope uses
- [Primary intended use 1]
- [Primary intended use 2]
- [Intended users: who is expected to use this and in what context]

### Out-of-scope uses
- [Use this model is NOT validated for]
- [Use that is explicitly prohibited]
- [High-stakes context where this model must not be the sole decision-maker]

---

## 3. Training Data Summary

| Field | Value |
|---|---|
| Data sources | [SOURCES] |
| Size / volume | [N examples / tokens] |
| Time range of data | [START – END] |
| Languages / domains covered | [LANGUAGES_DOMAINS] |
| Known gaps or under-represented groups | [GAPS] |
| Datasheet reference | [link by name to the dataset's DATASHEET_TEMPLATE entry] |

> For the full provenance and collection process, reference the dataset's Datasheet (see `DATASHEET_TEMPLATE`).

---

## 4. Evaluation Data and Metrics

| Field | Value |
|---|---|
| Evaluation datasets | [EVAL_SETS] |
| Why these eval sets | [JUSTIFICATION — how they represent intended use] |
| Primary metrics | [METRIC_1, METRIC_2, ...] |
| Decision threshold(s) | [THRESHOLD] |

### Disaggregated / per-group results

<!-- Report metrics broken out by relevant group (e.g. demographic, language, segment) wherever the model could affect people differently. -->

| Group | [METRIC_1] | [METRIC_2] | N | Notes |
|---|---|---|---|---|
| Overall | [value] | [value] | [N] | |
| [Group A] | [value] | [value] | [N] | |
| [Group B] | [value] | [value] | [N] | |

---

## 5. Quantitative Analysis

- **Headline results**: [summary of overall performance against the bar]
- **Performance variation across groups**: [where disaggregated results diverge and by how much]
- **Confidence / calibration**: [calibration findings, error bars]
- **Comparison to baseline**: [vs prior version / vs simpler baseline]

---

## 6. Ethical Considerations

- **Sensitive data**: [does the model touch PII, protected attributes, or sensitive domains?]
- **Potential harms**: [who could be harmed and how if the model errs or is misused]
- **Fairness concerns**: [identified bias risks and what was done about them]
- **Human oversight**: [where a human must remain in the loop]
- **Misuse potential**: [foreseeable misuse and any mitigations]

---

## 7. Caveats and Recommendations

- [Caveat about generalization beyond the eval distribution]
- [Recommendation on monitoring in production]
- [Recommendation on retraining / staleness cadence]
- [Conditions under which results should not be trusted]

---

## 8. Known Limitations

| Limitation | Impact | Mitigation / guidance |
|---|---|---|
| [Limitation 1] | [impact] | [how users should compensate] |
| [Limitation 2] | [impact] | [mitigation] |
| [Limitation 3] | [impact] | [mitigation] |

---

## 9. Sign-off

| Role | Name | Status | Date |
|---|---|---|---|
| Model owner | [name] | [APPROVED / PENDING] | [date] |
| Responsible-AI / Ethics reviewer | [name] | [APPROVED / PENDING] | [date] |
| Security reviewer | [name] | [APPROVED / PENDING] | [date] |
