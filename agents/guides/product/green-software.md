# Green Software Guide

## Overview
The software industry contributes to roughly 2-4% of global greenhouse gas emissions (on par with the aviation industry). Green software engineering is an emerging discipline aimed at building applications that are carbon-efficient from day one. This guide serves as the foundation for the `green-software` skill.

## 1. The Core Metrics
You cannot improve what you cannot measure. Green software relies on the **Software Carbon Intensity (SCI) Specification**, developed by the Green Software Foundation.

### The Algorithm: `SCI = ((E * I) + M) per R`
- **E (Energy)**: Energy consumed by the software in kWh.
- **I (Carbon Intensity)**: Grams of carbon emitted per kWh of electricity (dependent on datacenter location and time of day).
- **M (Embodied Carbon)**: The carbon debt of the hardware resources allocated to running the software.
- **R (Functional Unit)**: How the software scales (e.g., per user, per API request, per video minute).

*Goal: Drive the SCI score down to zero.*

## 2. Six Principles of Green Software Engineering

1. **Carbon Efficiency**: Emit the least amount of carbon possible.
2. **Energy Efficiency**: Consume the least amount of electricity possible.
3. **Carbon Awareness**: Run workloads when and where the electricity is greenest. Use APIs from groups like *Electricity Maps* or *WattTime* to predict carbon intensity.
4. **Hardware Efficiency**: Use the least amount of embodied carbon possible. Maximize the lifespan of the hardware your application runs on (e.g., don't drop support for 3-year-old operating systems unnecessarily).
5. **Measurement**: Measure carbon using the SCI.
6. **Climate Commitments**: Understand the reduction mechanism (e.g., offsetting vs. absolute reduction).

## 3. Practical Architecture Patterns

### Demand Shaping
Instead of auto-scaling servers to meet peak demand at all costs (which often requires keeping idle "warm" servers running), Demand Shaping alters the behavior of the application based on grid carbon intensity.
- *Examples*: A video streaming app defaults to 720p instead of 4K when the local grid is powered by coal. A background analytics job pauses until the wind is blowing.

### Sustainable Web Design
- **Dark Mode**: OLED screens use significantly less battery power when displaying true black (`#000000`).
- **Media Optimization**: Serve lazy-loaded, WebP/AVIF images.
- **Bundle Size**: Minify JavaScript and CSS. Every byte sent over the network consumes energy across dozens of switches and routers.

## 4. How to Use the Green Software Skill
Invoke the `green-software` skill during the PR/Review phase or during an Architectural Audit. The agent will analyze your compute patterns and generate recommendations prioritizing energy and carbon efficiency using the `GREEN_SOFTWARE_REPORT_TEMPLATE.md`.
