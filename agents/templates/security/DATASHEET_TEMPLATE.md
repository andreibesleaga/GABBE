# Datasheet for Dataset: [DATASET_NAME]

<!-- Datasheet for Datasets in the Gebru et al. style. Fill every [PLACEHOLDER]. -->
<!-- Store in: docs/security/datasheets/[dataset-name]-datasheet.md -->
<!-- Pair this datasheet with the Model Card of any model trained on this data (see MODEL_CARD_TEMPLATE). -->

---

## 1. Motivation

- **For what purpose was the dataset created?** [PURPOSE — and what gap it fills]
- **Who created it and for whom?** [CREATOR_TEAM / commissioning entity]
- **Who funded the creation?** [FUNDING_SOURCE]
- **Any other context?** [NOTES]

---

## 2. Composition

- **What do the instances represent?** [e.g. documents, images, user events, conversations]
- **How many instances are there?** [TOTAL_COUNT, with breakdown by type/class if relevant]
- **Is it a sample or the full population?** [SAMPLE_OR_COMPLETE — and sampling method if a sample]
- **What data does each instance consist of?** [FIELDS / FEATURES]
- **Are there labels/targets?** [LABELS — and how derived]
- **Is any information missing?** [MISSINGNESS — and why]
- **Are relationships between instances made explicit?** [RELATIONSHIPS, e.g. threads, users]
- **Are there recommended splits?** [TRAIN/VAL/TEST splits and rationale]
- **Known errors, noise, or redundancy?** [QUALITY_ISSUES]
- **Does it contain confidential, sensitive, or PII data?** [SENSITIVE_DATA — categories and handling]
- **Could it identify individuals or sub-populations?** [IDENTIFIABILITY]

---

## 3. Collection Process

- **How was the data acquired?** [COLLECTION_METHOD — directly observed, reported, derived, scraped, purchased]
- **What mechanisms/tools were used?** [TOOLS / APIS / INSTRUMENTS]
- **Over what time frame was it collected?** [START – END]
- **Who collected it?** [COLLECTORS — staff, crowdworkers, automated]
- **Were collectors compensated fairly?** [COMPENSATION, if human]
- **Was consent obtained?** [CONSENT_BASIS — and from whom]
- **Were individuals notified / given a way to revoke?** [NOTICE_AND_REVOCATION]
- **Was an ethics/IRB review conducted?** [ETHICS_REVIEW]

---

## 4. Preprocessing, Cleaning, and Labeling

- **What preprocessing was done?** [TOKENIZATION / NORMALIZATION / FILTERING / DEDUP]
- **Was raw data saved?** [RAW_RETAINED — and where]
- **How was labeling performed?** [LABELING_PROCESS — annotators, guidelines, tooling]
- **Inter-annotator agreement / quality control?** [QC_METRICS]
- **What was filtered out, and could that introduce bias?** [FILTERING_BIAS]
- **Is the preprocessing software available?** [SOFTWARE_AVAILABILITY]

---

## 5. Uses

- **What has the dataset been used for so far?** [PRIOR_USES]
- **What tasks is it appropriate for?** [APPROPRIATE_USES]
- **What tasks should it NOT be used for?** [INAPPROPRIATE_USES]
- **Does its composition limit fair/safe use?** [COMPOSITION_RISKS — e.g. group under-representation]
- **What should a future user know to avoid misuse?** [USER_GUIDANCE]

---

## 6. Distribution

- **Will it be distributed beyond the creating entity?** [DISTRIBUTION_SCOPE]
- **How will it be distributed?** [CHANNEL / FORMAT]
- **Under what license / terms of use?** [LICENSE]
- **Any IP, export, or regulatory restrictions?** [RESTRICTIONS]
- **When will it be released?** [RELEASE_DATE]

---

## 7. Maintenance

- **Who maintains the dataset?** [MAINTAINER + CONTACT]
- **How will errors be reported and corrected?** [ERROR_PROCESS]
- **Will it be updated? On what cadence?** [UPDATE_CADENCE]
- **Are there retention limits / deletion obligations?** [RETENTION_POLICY]
- **How are older versions kept and communicated?** [VERSIONING]
- **Can others extend/build on it, and how is that validated?** [CONTRIBUTION_PROCESS]

---

## 8. Sign-off

| Role | Name | Status | Date |
|---|---|---|---|
| Dataset owner | [name] | [APPROVED / PENDING] | [date] |
| Privacy / data-protection reviewer | [name] | [APPROVED / PENDING] | [date] |
| Ethics reviewer | [name] | [APPROVED / PENDING] | [date] |
