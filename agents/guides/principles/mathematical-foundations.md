# Mathematical Foundations for Software Engineering

Mathematics is the quiet substrate under most of what software engineers do well. You rarely write a proof at
work, but the *habits* of mathematical reasoning — precise definitions, invariants, case analysis, reasoning
about scale — are what separate code that happens to pass its examples from code that is correct by
construction. This guide is a reference for the mathematical topics that the SWEBOK v4 "Mathematical
Foundations" knowledge area treats as core, and for each one it points at where the idea actually surfaces in
day-to-day engineering. It is a foundations reference, not a course; the goal is recognition and orientation,
not derivation.

## Propositional and predicate logic

Logic is the algebra of true/false statements and of statements quantified over values ("for all", "there
exists"). Propositional logic gives you `and`/`or`/`not`/`implies` and their identities; predicate logic adds
quantifiers and variables.

Where it shows up: every boolean condition, guard, and short-circuit you write is propositional logic, and
getting De Morgan's laws right is the difference between a correct negation and a subtle bug. More deeply,
**invariants** — properties that must hold for all valid states — are predicate-logic statements over your
program's data. This is exactly the raw material of property-based testing: an invariant like "decode of
encode is the identity for all inputs" is a quantified logical claim, and `pbt-strategy.skill` exists to
generate inputs that try to falsify it. Preconditions, postconditions, and loop invariants are the same idea
applied to a single function.

## Sets, relations, and functions

A set is an unordered collection of distinct elements; a relation is a set of tuples linking elements; a
function is a relation that maps each input to exactly one output. Operations like union, intersection,
difference, and the notions of injective/surjective/bijective are the vocabulary.

Where it shows up: collections and deduplication are set operations; database joins, foreign keys, and
many-to-many tables are relations made concrete; referential integrity is a constraint on a relation. Knowing
that a function must be single-valued is what tells you when a mapping is actually ambiguous, and knowing when
a relation is an equivalence relation is what justifies partitioning data into clean, non-overlapping classes.

## Graphs and trees

A graph is a set of nodes connected by edges (directed or undirected, weighted or not); a tree is a connected
acyclic graph with a hierarchy. Reachability, cycles, topological order, and shortest paths are the standard
questions.

Where it shows up: dependency analysis is graph work end to end. Build graphs, module import graphs, and
package dependency trees must be acyclic, and detecting a cycle is detecting a design problem; topological
sort is what produces a valid build or migration order. Call graphs, state machines, data-flow graphs, and
the object graphs a garbage collector traces are all graphs. Trees underlie file systems, the DOM, ASTs in
compilers, and most index structures.

## Combinatorics

Combinatorics counts configurations: permutations, combinations, the multiplication and addition principles,
and the explosion of states as independent choices multiply.

Where it shows up: it is the backbone of **test-case design**. The number of combinations of input
conditions is combinatorial, which is precisely why exhaustive testing is usually infeasible and why
techniques like equivalence partitioning, boundary-value analysis, and pairwise (all-pairs) testing exist —
they are combinatorial reduction strategies that cover the interactions that matter without enumerating the
full product. Combinatorics also explains why feature-flag and configuration matrices blow up so fast, and
why caching keyed on many dimensions has a huge possible key space.

## Probability and statistics

Probability quantifies uncertainty; statistics infers from samples to populations. Distributions,
expectation, variance, percentiles, significance, effect size, and confidence intervals are the working
tools.

Where it shows up: estimation is probabilistic, not deterministic — the P50/P90 ranges in
`estimation-sizing.skill` are percentiles of an outcome distribution, and treating them as such is what keeps
an estimate honest. Tail latencies (p95, p99) are percentiles of a response-time distribution and matter far
more than the mean for user experience. Reasoning about benchmark noise, A/B-test outcomes, sampling, and
"is this difference real or noise?" is statistical inference, which is the territory of
`empirical-methods.skill`. The central honesty rule travels with the math: an association is not a cause, and
a significant result is not necessarily an important one.

## Proof techniques and formal reasoning

The standard proof methods — direct proof, proof by contradiction, proof by cases, and especially
mathematical induction — are ways to establish that a claim holds for *all* cases rather than the few you
tried.

Where it shows up: induction is the natural way to reason about recursion and about loops (the inductive step
is the loop body preserving the invariant). Reasoning by cases is what makes exhaustive `switch`/`match`
handling and total functions trustworthy. Formal methods and lightweight specification push this further,
proving properties of a design before code exists; even without full formality, the *posture* — define
precisely, then argue every case is covered — is what produces robust software.

## Asymptotics and Big-O

Asymptotic analysis (Big-O, Big-Theta, Big-Omega) describes how cost grows with input size, abstracting away
constants and hardware. It is part discrete math, part analysis, and it is the lens for scalability.

Where it shows up: choosing the data structure or algorithm whose growth rate survives your real input sizes
is the everyday application, and it is owned in execution by `time-complexity.skill`. The math here tells you
*why* an O(n^2) inner loop that is fine in a test becomes an outage at production scale, and why constant
factors still matter once two options share the same asymptotic class.

## Honest scope note

This is a foundations *reference*, not a mathematics course. Each topic above is a doorway: the entries name
the concept and show where it lands in engineering so you can recognize it and reach for the right execution
skill (`pbt-strategy.skill`, `estimation-sizing.skill`, `empirical-methods.skill`, `time-complexity.skill`,
and the test-design practices). It does not teach the underlying theorems, derivations, or formal notation —
for genuine depth, consult dedicated texts in discrete mathematics, probability, and the theory of
computation. The aim here is fluency in *where the math matters*, not a substitute for learning the math.
