# Legacy System Audit: [System Name]

**Language**: [COBOL / Fortran / VB6 / Delphi]
**Age**: [X Years]
**Criticality**: [High - $XM/day flows through this]

## 1. Knowledge Risk (Bus Factor)
-   **Who knows how this works?**: [Name(s) / "No one"]
-   **Documentation Status**: [None / Outdated / Good]
-   **Bus Factor Score**: [1-5 (1 = Only one person knows)]

## 2. Technical Health
-   **Source Code Availability**: [Yes / Partial / Lost (Binary only)]
-   **Build Process**: [Automated / Manual Scripts / "Don't touch it"]
-   **Test Coverage**: [None / Manual / Automated Unit Tests]
-   **Database**: [DB2 / VSAM / Flat Files / Oracle 8i]

## 3. Coupling Analysis
-   **Inbound Dependencies**: [Who calls us?]
-   **Outbound Dependencies**: [Who do we call?]
-   **Hard Dependencies**: [Mainframe hardware / Specific OS version]

## 4. Modernization Strategy
**Selected Strategy**: [Retain / Encapsulate / Refactor / Replatform]

### Phase 1: Stabilization
-   [ ] Create "Golden Master" test suite (capture I/O)
-   [ ] Dockerize build environment (if possible)
-   [ ] Document core business rules

### Phase 2: Strangulation (Optional)
-   [ ] Identify first slice to migrate (e.g., "Customer Lookup")
-   [ ] Build Anti-Corruption Layer (ACL)
-   [ ] Route traffic to new service
