# Deployment Configuration Snippets

Copy the relevant section to your project root.

---

## 1. Vercel (`vercel.json`)
Use for frontend frameworks (Next.js, React, Vue) and Serverless Functions.

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://api.example.com/:path*" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" }
      ]
    }
  ],
  "regions": ["iad1"],
  "cleanUrls": true
}
```

---

## 2. Railway (`railway.toml`)
Use for backend services (Node, Go, Python, Docker) and Databases.

```toml
[build]
builder = "nixpacks"
buildCommand = "npm run build"

[deploy]
startCommand = "npm start"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on-failure"

[service]
name = "my-backend-service"
```

---

## 3. SST (`sst.config.ts`)
Use for AWS Serverless (Lambda, DynamoDB, API Gateway).

```typescript
import { SSTConfig } from "sst";
import { NextjsSite, Table } from "sst/constructs";

export default {
  config(_input) {
    return {
      name: "my-sst-app",
      region: "us-east-1",
    };
  },
  stacks(app) {
    app.stack(function Site({ stack }) {
      const table = new Table(stack, "Notes", {
        fields: {
          pk: "string",
          sk: "string",
        },
        primaryIndex: { partitionKey: "pk", sortKey: "sk" },
      });

      const site = new NextjsSite(stack, "site", {
        bind: [table],
      });

      stack.addOutputs({
        SiteUrl: site.url,
      });
    });
  },
} satisfies SSTConfig;
```
