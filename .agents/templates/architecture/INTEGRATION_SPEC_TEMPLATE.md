# Integration Specification: [Integration Name]

**Type**: [Inbound / Outbound / Bi-directional]
**External System**: [Salesforce / SAP / Stripe / Partner API]
**Protocol**: [REST / SOAP / FTP / Queue]

## 1. Business Context
[Why are we integrating? What value does this provide?]

## 2. Data Mapping
| Our Field | External Field | Transformation Rules |
|---|---|---|
| `user.email` | `Contact.Email` | Lowercase |
| `user.id` | `Contact.ExternalId__c` | |
| `order.status` | `Opportunity.StageName` | Map: Paid -> Closed Won |

## 3. Integration Pattern
-   **Pattern**: [Real-time / Batch / Event-Driven]
-   **Trigger**: [User Action / Nightly Job / Webhook]
-   **Direction**: [Push to External / Pull from External]

## 4. Authentication & Security
-   **Method**: [OAuth2 / API Key / mTLS / VPN]
-   **Credentials**: [Stored in Secrets Manager]
-   **Network**: [Whitelisting IPs required?]

## 5. Resilience & Performance
-   **Rate Limits**: [External system limit: 100 req/min]
-   **Throttling**: [Our implementation: Max 80 req/min]
-   **Retry Policy**: [Exp. backoff up to 1 hour]
-   **Circuit Breaker**: [Trip after 50% errors in 1 min]

## 6. Error Handling
| Error Scenario | Action | Alert |
|---|---|---|
| Auth Failure | Stop & Alert | P1 |
| Validation Error | Log to DLQ | P3 |
| Timeout | Retry (3x) | - |
