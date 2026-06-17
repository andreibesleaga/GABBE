# Software Engineering Models and Methods

A model is a deliberate simplification of a system built to answer a specific question — "what are the
entities and how do they relate?", "what happens when this event arrives?", "how do these services
communicate?". A method is a disciplined procedure for building and using such models. Engineers model
constantly, usually informally on a whiteboard; this guide supplies the taxonomy underneath that practice so
you can choose the right model type, language, and degree of rigor on purpose rather than by reflex. It is
grounded in the SWEBOK v4 "Software Engineering Models and Methods" knowledge area and is meant as the
method-selection spine that sits behind the hands-on modeling skills.

## Model types: information, structural, behavioral

Models fall into three broad families by the question they answer.

- **Information models** describe the data: the entities, their attributes, and the relationships and
  constraints among them — independent of any behavior. Entity-relationship models and domain models live
  here; they answer "what does the system know about, and what are the rules on that knowledge?". This is the
  core of `domain-model.skill`.
- **Structural models** describe the static composition: components, modules, services, their interfaces, and
  how they are arranged and depend on one another. Component, package, and deployment views, and C4's context
  and container levels, are structural; they answer "what are the parts and how are they wired?". This is the
  territory of `systems-architecture.skill`.
- **Behavioral models** describe dynamics over time: states and transitions, sequences of interaction,
  control flow, and processes. State machines, sequence diagrams, activity flows, and BPMN processes are
  behavioral; they answer "what happens, in what order, in response to what?".

A real design usually needs one model from more than one family — an information model of the data, a
structural model of the components, and a behavioral model of the critical flows — because each hides what the
others reveal.

## Modeling languages

Languages give models a shared, communicable vocabulary. The common ones map cleanly onto the model types:

- **UML** (Unified Modeling Language) is the broad general-purpose set: class diagrams (information/
  structural), component and deployment diagrams (structural), and sequence, state, and activity diagrams
  (behavioral). Powerful but easy to over-apply.
- **C4** is a lightweight structural notation with four zoom levels — system Context, Container, Component,
  and Code — designed to keep architecture diagrams legible to mixed audiences. It is well suited to
  `systems-architecture.skill`.
- **ER** (entity-relationship) models data structure and is the natural language for information models and
  the bridge to relational schema design.
- **BPMN** (Business Process Model and Notation) is a behavioral language specialized for business processes,
  workflows, and the hand-offs between roles and systems.

The rendering mechanics — diagram-as-code, tooling, and house style — are owned by `diagramming.skill` and
the conventions in the guide `principles/diagramming-standards.md`; this guide is about which *language* fits
which *question*, not how to draw it.

## Formal, semi-formal, and informal methods

Methods sit on a spectrum of rigor, and the spectrum is a cost/precision trade-off.

- **Informal methods** use natural language, sketches, and ad-hoc diagrams. Cheap, fast, excellent for
  communication and early exploration — but ambiguous and unverifiable. Most whiteboard work is here, and for
  most situations that is the right level.
- **Semi-formal methods** use a defined notation with structure but without complete mathematical semantics —
  UML, C4, ER, BPMN. They constrain ambiguity and enable shared review and some tooling, while staying
  approachable. This band covers the large majority of practical modeling need.
- **Formal methods** use mathematically precise specification languages (for example state-based or
  algebraic specifications, model checkers, theorem provers) with defined semantics that permit proof and
  automated verification. They can demonstrate properties hold for *all* cases — invaluable for
  safety-critical, concurrent, or protocol-level designs where a missed case is catastrophic — but they are
  expensive in skill, time, and maintenance.

The honest rule is that rigor should match the cost of being wrong. Reach for formal methods where failure is
unacceptable and the design is small and critical enough to be tractable; stay semi-formal or informal
everywhere else.

## Method-selection criteria

Choosing a model and method is itself a small engineering decision. Weigh:

- **Cost of error.** Higher stakes (safety, money, security, irreversible effects) justify more rigor; a
  throwaway internal tool does not.
- **Audience.** Mixed or non-technical stakeholders favor C4 context views and informal sketches; an
  implementation team can use detailed UML or formal specs.
- **Question being asked.** Match the model family to the question — information, structural, or behavioral —
  and resist modeling dimensions nobody needs to decide on.
- **Longevity and maintenance.** A model that must stay accurate over time costs upkeep; informal sketches
  rot fast, formal specs demand discipline to keep true. Prefer the lightest model that survives as long as
  it must.
- **Tooling and verifiability.** Use formal or strongly-typed models where you actually intend to verify or
  generate from them; otherwise the added precision is overhead.

The default is to model the minimum that resolves the open question at the lowest rigor that is still
unambiguous enough — and to escalate rigor only where the cost of being wrong demands it.

## Honest scope note

In practice, most modeling need is already met by two skills: `domain-model.skill` for the information model
of the domain and `diagramming.skill` (with `systems-architecture.skill` and the
`principles/diagramming-standards.md` conventions) for structural and behavioral views. This guide does not
duplicate that hands-on work; it adds the method-taxonomy spine — the model-type families, the language map,
the formality spectrum, and the selection criteria — so that the choice of *which* model and *how much* rigor
is made deliberately. It is an orientation reference, not a tutorial in UML, formal specification, or any
single notation; for depth in a specific language or formal technique, consult dedicated material.
