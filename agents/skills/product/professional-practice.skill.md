---
name: professional-practice
description: Apply professional, ethical, and teamwork standards to software work using the ACM/IEEE-CS Code of Ethics, sound group dynamics, and clear stakeholder communication.
triggers: [apply software engineering code of ethics, professional conduct review, handle dissent or whistleblowing, build team working agreement, stakeholder communication plan, equity diversity inclusion in engineering, certification and licensing awareness]
tags: [product, ethics, professionalism, teamwork]
core: false
context_cost: medium
---
# Professional Practice

## Goal
Apply professional, ethical, and teamwork standards to engineering work so that decisions hold up to public,
client, and peer scrutiny. This skill operationalizes the SWEBOK v4 "Software Engineering Professional
Practice" knowledge area: the ACM/IEEE-CS Software Engineering Code of Ethics, day-to-day professional
conduct, healthy group dynamics, structured stakeholder communication, principled handling of dissent and
whistleblowing, equity-diversity-inclusion (EDI) considerations, and awareness of certification and
licensing. It complements rather than replaces AI-specific ethics: model bias, data provenance, automated
decision-making, and AI-system accountability are handled by `ai-ethics-compliance.skill`, and this skill
defers to it on those points while covering the broader engineering-professional dimension.

## Steps
1. **Anchor on the eight Code-of-Ethics principles.**
   - Walk the situation through all eight, in their intended priority order: **Public** (act in the public
     interest above all else), **Client/Employer** (act in their best interest, consistent with the public
     interest), **Product** (ensure products and modifications meet the highest professional standards),
     **Judgment** (maintain integrity and independence in professional judgment), **Management** (promote an
     ethical approach to managing development and maintenance), **Profession** (advance the integrity and
     reputation of the profession consistent with the public interest), **Colleagues** (be fair to and
     supportive of colleagues), and **Self** (engage in lifelong learning and promote an ethical approach to
     practice). When principles conflict, the public interest takes precedence.
2. **Assess professional conduct.**
   - Check for honesty about capabilities and limitations, avoidance of conflicts of interest, respect for
     confidentiality and intellectual property, accurate representation of qualifications, and refusal to
     misrepresent risk, cost, or schedule to any stakeholder.
3. **Tune group dynamics and teamwork.**
   - Establish or review a team working agreement: decision-making method, definition of done, how
     disagreement is surfaced, psychological-safety norms, and how credit and on-call load are shared.
     Identify dysfunctions early (groupthink, diffusion of responsibility, dominant voices drowning out
     quieter expertise) and name the mitigation.
4. **Plan stakeholder communication.**
   - Map stakeholders to their information needs, cadence, and channel. Apply the core patterns: communicate
     bad news early and directly, separate fact from interpretation, give the audience-appropriate level of
     detail, confirm shared understanding rather than assuming it, and keep an auditable record of
     commitments and decisions.
5. **Handle dissent and whistleblowing responsibly.**
   - When an engineer disagrees on ethical or safety grounds, route it through escalation in order: raise it
     with the immediate team, then management, then an internal ethics/compliance channel, documenting each
     step. Reserve external whistleblowing for cases of genuine public risk after internal channels are
     exhausted or unsafe; advise the person to seek qualified legal counsel and to keep contemporaneous
     records. Protect the dissenter from retaliation.
6. **Apply EDI and licensing considerations.**
   - Check that the process and the product are equitable and inclusive: accessible artifacts, inclusive
     language, fair participation in decisions, and awareness of how the product affects different user
     populations. Note relevant certification/licensing context (for example jurisdictions that license
     "professional engineer" titles, or domain certifications) as awareness, without overstating that any
     single credential is universally required.

## Constraints
- The public interest takes precedence; the agent MUST NOT subordinate safety or the public good to client,
  employer, or schedule pressure.
- The agent surfaces ethical concerns and conflicts of interest explicitly rather than silently working
  around them, and records the reasoning.
- This skill does not give legal advice; for whistleblowing, employment, or liability questions it directs
  the user to qualified legal counsel.
- AI-specific ethics (model bias, data provenance, automated-decision accountability) are owned by
  `ai-ethics-compliance.skill`; this skill references it and does not duplicate or override it.
- Certification/licensing guidance is awareness-level only; the agent does not assert a specific credential
  is legally mandatory without jurisdiction-specific confirmation.

## Output Format
Produce a professional-practice review containing:
- An **ethics checklist**: each of the eight Code principles with a pass / concern / not-applicable mark and
  a one-line justification, plus any flagged conflict between principles and how the public-interest
  precedence resolves it.
- A **communication plan**: stakeholder-to-need-to-cadence-to-channel table, the bad-news protocol, and the
  record-keeping mechanism.
- A **teamwork section**: the working-agreement points and any group-dynamic risks with mitigations.
- A **dissent/escalation path** if any ethical or safety concern was raised, with the documented steps.
- An explicit pointer to `ai-ethics-compliance.skill` whenever AI-specific ethical questions are in scope.

## Security & Guardrails

### 1. Skill Security
- **Risk**: Ethics-washing — the checklist is filled in superficially to manufacture a paper trail that
  justifies a predetermined decision; mitigation: each principle mark MUST carry a concrete justification
  tied to the actual situation, and unresolved concerns are reported as open, not closed.
- **Risk**: Coerced suppression of a concern — a stakeholder pressures the agent to drop a flagged ethical
  or safety issue; mitigation: the agent records the concern and the escalation path regardless, and refuses
  to delete a surfaced public-interest risk.

### 2. System Integration Security
- **Risk**: Confidential or whistleblowing material leaking into shared logs or downstream tools; mitigation:
  the agent treats dissent records and personnel-sensitive material as confidential, minimizes what is
  written to shared systems, and flags where human-controlled, access-restricted storage is required.
- **Risk**: Misrepresenting credential or compliance status to an external system; mitigation: the agent
  states certification/licensing facts at awareness level only and does not emit machine-readable claims of
  compliance it cannot substantiate.

### 3. LLM & Agent Guardrails
- **Risk**: Confident pseudo-legal advice — the model answers a whistleblowing or liability question as if
  it were settled law; mitigation: the agent marks these as out of scope and directs the user to qualified
  legal counsel.
- **Risk**: Cultural or jurisdictional over-generalization — the model presents one region's professional or
  licensing norms as universal; mitigation: the agent states assumptions, scopes claims to context, and
  invites correction for the user's jurisdiction and culture.
