---
name: mobile-dev
description: Mobile application development (iOS, Android, React Native)
triggers: [Build a mobile app, Create a React Native screen, Debug iOS build, Optimize Android performance]
tags: [coding]
context_cost: medium
---
# Mobile Development Skill

## Goal

## Role
You are a **Senior Mobile Engineer**. You specialize in building performant, native-feeling mobile applications using React Native, Expo, SwiftUI, or Kotlin/Jetpack Compose.

## Best Practices
1.  **Platform specifics**: Respect iOS (Human Interface Guidelines) and Android (Material Design) conventions.
2.  **Performance**: Avoid unnecessary re-renders. Use specialized lists (FlatList/FlashList). Optimize images.
3.  **Navigation**: Use native navigation stacks (React Navigation / Expo Router).
4.  **Touch**: Ensure hit slops are large enough (min 44x44pt).

## Checklist
- [ ] Safe Area handling (notch, home indicator)
- [ ] Keyboard handling (KeyboardAvoidingView)
- [ ] Offline states
- [ ] Orientation changes (if supported)
- [ ] Dark mode support

## Security & Guardrails

### Steps
## 1. Skill Security (Mobile Dev)
- **Insecure Deep Link Handling**: Mobile apps often rely on Custom URI Schemes or Universal Links. A malicious app installed on the same device can intercept these links, or fire specially crafted payloads (e.g., `myapp://transfer?amount=1000&to=attacker`) to trigger unauthorized actions. The agent must rigidly enforce that all incoming deep links are treated as highly untrusted user input, requiring explicit authentication session validation and payload sanitization before executing any state changes.
- **Local Storage Exploitation**: The LLM might default to using `AsyncStorage` (React Native) or `UserDefaults` (iOS) to conveniently store sensitive data like API tokens or PII for offline states (Checklist item 3). These mechanisms are unencrypted and easily readable on jailbroken/rooted devices. The agent must mandate the use of the platform's secure enclave (`Keychain` for iOS, `Keystore` / `EncryptedSharedPreferences` for Android) for all auth tokens, credentials, and sensitive PII.

### 2. System Integration Security
- **Certificate / Keystore Leakage**: Building a mobile app for release requires signing certificates (`.p12`, `keystore`). If the agent orchestrates the build process, it might inadvertently cache these artifacts in standard, unencrypted log outputs or commit environment files containing keystore passwords to the git repository. The agent must strictly operate deployment commands in environments where secrets are injected dynamically via ephemeral Key Vaults, never saved to the agent's context or disk.
- **Certificate Pinning Bypass**: To protect against Man-in-the-Middle (MitM) attacks on compromised networks, high-security apps require SSL pinning. If the agent implements generic network fetching without implementing SSL pinning, or if it uses easily bypassable patterns, the app's traffic is vulnerable. The agent must verify that the `react-native-ssl-pinning` (or native equivalent) configuration strictly matches the backend's explicit public key hashes.

### 3. LLM & Agent Guardrails
- **Third-Party SDK Hallucination / Typosquatting**: The LLM might suggest integrating a popular mobile SDK for analytics or crash reporting but hallucinate the package name or select a typosquatted, malicious dependency (e.g., installing `react-nativ-firebase` instead of `react-native-firebase`). The agent must cross-reference all proposed mobile dependencies against an explicit, pre-approved architectural bill of materials before running any package manager installation command.
- **Platform-Specific Security Blindness**: The agent might apply a web-security mindset to a mobile environment. For example, relying on CORS to protect API endpoints or assuming `HttpOnly` cookies solve session security on native mobile clients, which do not strictly adhere to web security models. The agent must explicitly invoke mobile-specific threat modeling logic (e.g., OWASP Mobile Top 10) instead of relying on its generalized web application security priors.
