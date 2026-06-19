# The Undying Tech Stack: Legacy Systems in 2026

Legacy systems are not "dead" code. They are "proven" code.

> **Context**: As of 2026, a large share of the world's banking and payment transactions
> still touch a mainframe, and COBOL remains pervasive in core banking and ATM networks.
> The often-quoted "95% of ATM swipes run COBOL" figure traces to a 2017 Reuters report
> attributed to industry estimates and has not been rigorously verified — treat it as a
> widely-cited illustration of COBOL's footprint, not a precise measurement.

## 1. The Critical Stack

### COBOL (Common Business Oriented Language)
-   **Why it survives**: Unmatched decimal precision (money handling) and massive throughput.
-   **Where lies**: Core Banking, Insurance Claims, Government (IRS/Social Security).
-   **Risk**: Talent shortage. The average COBOL dev is 55+ years old.

### Fortran (Formula Translation)
-   **Why it survives**: Speed. For certain dense numerical/array workloads it can match or beat naively-written C/C++ — partly because Fortran's lack of pointer aliasing lets compilers optimize array loops more aggressively, and because of decades of highly-tuned numerical libraries (BLAS/LAPACK). With equivalent effort and modern compilers, C/C++ is competitive; the advantage is workload- and code-specific, not absolute.
-   **Where lies**: Weather forecasting, Nuclear simulation, Aerospace (NASA/Boeing).

### Mainframe (IBM Z-Series)
-   **Why it survives**: Reliability (5 9s default). Vertical scaling (adding CPUs while running). Security (Hardware encryption).
-   **Modern**: Z-Series now runs Linux and OpenShift (K8s) alongside legacy z/OS.

## 2. Modernization Strategies "In Place"

### The "Mullet" Architecture
-   **Front:** Modern Web/Mobile (React/iOS).
-   **Back:** Legacy Mainframe.
-   **Glue:** API Gateway / Middleware.

### Zowe (Modern Mainframe DevOps)
The **Open Mainframe Project** created **Zowe**, which opens the mainframe to modern tools:
-   **CLI**: Control mainframe via command line (not green screen).
-   **API Mediation Layer**: Securely expose z/OS services as REST APIs.
-   **Explorer**: VS Code extension to edit COBOL/JCL remotely.

## 3. How to Read COBOL (Crash Course)

COBOL is verbose. It reads like English.

```cobol
IDENTIFICATION DIVISION.
PROGRAM-ID. HELLO-WORLD.

DATA DIVISION.
WORKING-STORAGE SECTION.
01 WS-NAME PICTURE X(20).

PROCEDURE DIVISION.
    DISPLAY "ENTER NAME: ".
    ACCEPT WS-NAME.
    DISPLAY "HELLO, " WS-NAME.
    STOP RUN.
```

-   **DIVISIONS**: The 4 major blocks (ID, ENV, DATA, PROCEDURE).
-   **PICTURE (PIC)**: Defines data types. `9(5)` = 5 digit integer. `X(20)` = 20 char string. `V99` = 2 decimal places.

## 4. Risk Mitigation Checklist

1.  **Identify the "Bus":** If Bob is the only one who knows the billing module, Bob is a single point of failure. **Pair program with Bob immediately.**
2.  **Characterization Tests:** Before fixing a bug, write a script that sends 1000 inputs and records 1000 outputs. Ensure your fix doesn't change outputs for non-bug inputs.
3.  **Documentation:** Use AI to generate explanation docs for complex subroutines.
