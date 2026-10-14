# Design Pattern Usage

**Pattern Name**: [e.g., Strategy Pattern]
**Component/File**: [e.g., `PaymentProcessor.ts`]

## 1. The Problem
[Describe the problem that led to choosing this pattern. e.g., "We had a switch statement growing out of control for payment methods."]

## 2. The Solution
[Explain how the pattern solves it. e.g., "We extracted each payment method into its own class implementing a common interface."]

## 3. Implementation Details
- **Context**: [The class using the strategy]
- **Interface**: [The common interface]
- **Concretions**: [List of concrete implementations]

## 4. Trade-offs
**Pros**:
- [e.g., Open/Closed principle followed]
- [e.g., Easier to test individual strategies]

**Cons**:
- [e.g., Increased number of classes]
- [e.g., Clients must know which strategy to select]
