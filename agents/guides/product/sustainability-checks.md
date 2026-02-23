# Sustainability & ESG Engineering Guide

## 1. Introduction
Sustainability in software engineering goes beyond recycling office paper; it concerns the direct energy consumption of our algorithms, the embodied carbon of the servers we rent, and the social impact of the software we deploy. This guide aligns engineering with Corporate ESG (Environmental, Social, Governance) mandates.

## 2. The Three Pillars of Green Software

### Energy Efficiency
Software consumes electricity. The goal is to consume less electricity per logical operation.
- **Algorithmic Efficiency**: Big-O notation matters for the planet. An O(n^2) algorithm wastes exponentially more energy than an O(n log n) one at scale.
- **Data Efficiency**: Transferring data across networks requires physical routers and switches to work harder. Compress assets, use smaller image formats (WebP/AVIF), and prune unused JSON payload fields.

### Hardware Efficiency
The manufacturing and disposal of servers (Embodied Carbon) often outweighs the electricity they use over their lifetime.
- **High Utilization**: A server running at 10% capacity consumes almost the same baseline power as one at 80%. Consolidate workloads using Kubernetes, Docker, or VMs.
- **Lifespan Extension**: Design software that functions well on older hardware (e.g., older Android devices, 5-year-old laptops) to delay e-waste.

### Carbon Awareness
Electricity grid greenness fluctuates based on weather (wind/solar) and time of day.
- **Spatial Shifting**: Deploy workloads to cloud regions powered by renewables (e.g., Iceland, specific AWS/GCP green zones).
- **Temporal Shifting**: Schedule heavy, non-urgent batch jobs (like ML training or DB backups) during periods when the local grid relies on excess renewable energy.

## 3. Social & Governance (The S and G in ESG)
- **Accessibility (A11y)**: Sustainable software must be usable by all. Ensure WCAG compliance so users with disabilities are not excluded.
- **Algorithmic Bias**: Audit AI or sorting algorithms to ensure they do not discriminate against minorities or disadvantaged groups.
- **Data Minimization**: Only collect what you need. Less data is better for privacy (Governance) and requires less storage (Environmental).

## 4. Agentic Workflow
Use the `sustainability-checks` skill to have an agent continuously audit PRs for energy waste. The agent will output a `GREEN_SOFTWARE_REPORT_TEMPLATE.md`.
