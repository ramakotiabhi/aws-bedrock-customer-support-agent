# AgentCore Project

This project was created with the [AgentCore CLI](https://github.com/aws/agentcore-cli).

## Project Structure

```
my-project/
├── AGENTS.md               # AI coding assistant context
├── agentcore/
│   ├── agentcore.json      # Project config (agents, memories, credentials, gateways, evaluators)
│   ├── aws-targets.json    # Deployment targets (account + region)
│   ├── .env.local          # Secrets — API keys (gitignored)
│   ├── .llm-context/       # TypeScript type definitions for AI assistants
│   │   ├── agentcore.ts    # AgentCoreProjectSpec types
│   │   └── aws-targets.ts  # Deployment target types
│   └── cdk/                # CDK infrastructure (@aws/agentcore-cdk)
├── app/                    # Agent application code
└── evaluators/             # Custom evaluator code (if any)
```

## Getting Started

```markdown
# Customer Support AI Agent with Amazon Bedrock AgentCore

## Project Summary
This project implements an enterprise-grade AI Customer Support Agent deployed on AWS Bedrock AgentCore using the Strands Agents framework. The agent resolves customer inquiries through real-time order tracking, refund initiation, knowledge base vector searches, deterministic loyalty program calculation via a secure sandboxed environment, and cross-session customer memory retention.

---

## Architecture Overview


```

```
                      +-----------------------------------+
                      |      Customer / Client API        |
                      +-----------------+-----------------+
                                        |
                                        v
                      +-----------------------------------+
                      |   Amazon Bedrock AgentCore        |
                      |     (MicroVM / Runtime)           |
                      +-----------------+-----------------+
                                        |
                                        v

```

+-----------------------------------------------------------------------------------+
|                            Strands Agent Core Loop                                |
|                                                                                   |
|  Foundation Model: amazon.nova-pro-v1:0 (via Bedrock ConverseStream API)          |
|  Hooks: MemoryHook (retrieve_customer_context, save_support_interaction)          |
+--------+------------------+-------------------+------------------+----------------+
|                  |                   |                  |
v                  v                   v                  v
+--------------+   +--------------+   +---------------+   +--------------+
|  AgentCore   |   |   Bedrock    |   |     Code      |   |  AgentCore   |
|   Gateway    |   |  Knowledge   |   |  Interpreter  |   |   Browser    |
|  (MCP / HTTP)|   |  Base (RAG)  |   |   (Sandbox)   |   |    Tool      |
+-------+------+   +-------+------+   +-------+-------+   +-------+------+
|                  |                  |                   |
v                  v                  v                   v
Lambda Functions      Amazon S3 +        Discount /        Live Amazon.com

* order_tracker       OpenSearch       Points Math        Documentation
* refund_processor    Serverless        Execution

```

---

## AWS Infrastructure & Resource Configuration

| Resource | Identifier / Endpoint | Details |
|---|---|---|
| **Region** | `us-east-1` | AWS US East (N. Virginia) |
| **Foundation Model** | `amazon.nova-pro-v1:0` | Direct on-demand Bedrock model ID |
| **Knowledge Base ID** | `KFZVEX6FMZ` | Amazon Titan Embeddings v2 + OpenSearch Serverless |
| **Memory Resource ID** | `CustomerSupportMemory-jcUBDw4Jto` | Semantic facts & user preferences strategies |
| **Gateway Endpoint** | `https://customersupportgateway-oef4vsera6.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp` | MCP endpoint for order and refund tools |
| **Execution Role** | `AgentCore-CustomerSupport-ApplicationAgentMyAgentRu-sgoCiekBlTH9` | IAM role attached with project execution access |

---

## Memory Strategy & Strands Integration

To ensure reliable multi-session recall across distinct agent interactions, `MemoryHook` was built with key optimizations:
1. **Message Structure Normalization**: Handled both plain-string and block-list message formats used by Strands Agents.
2. **Context Deduplication**: Context injection ensures previously injected memory blocks are not repeatedly duplicated into prompt history.
3. **Thinking Tag Elimination**: Reasoning tags (`<thinking>...</thinking>`) are filtered prior to saving to prevent noisy vector indexing.
4. **Dual Namespace Isolation**:
   - `cs_agent/{actorId}/facts`: Stores semantic entity extractions.
   - `cs_agent/{actorId}/preferences`: Stores declared customer preferences (e.g., communication channels and devices).

---

## Verification Test Scenarios

### Scenario 1: Order Tracking
```bash
agentcore invoke '{"prompt": "Where is my order ORD-001?", "customer_id": "CUST-123", "session_id": "session-1"}'

```

**Response:**

```json
{
  "response": "Your order ORD-001 for an Echo Dot (5th Gen, Charcoal) is currently in transit with UPS. The tracking number is 1Z999AA10123456784, and the estimated delivery date is October 28, 2024.\n"
}
<img width="1508" height="117" alt="Screenshot 2026-09-21 215055" src="https://github.com/user-attachments/assets/bb052fb0-8e01-4a83-9587-7d47241ce89d" />

```

---

### Scenario 2: Refund Processing

```bash
agentcore invoke '{"prompt": "I want to initiate a refund for order ORD-002 with amount 139.99 because the Kindle Paperwhite was damaged.", "customer_id": "CUST-123", "session_id": "session-1"}'

```

**Response:**

```json
{
  "response": "Your refund for order ORD-002 has been successfully processed. The refund amount is $139.99 and it will be returned to your original payment method within 3-5 business days. The refund ID is REF-2024-8841. If you have any further questions, feel free to ask.\n"
}

```

---

### Scenario 3: Knowledge Base RAG Query

```bash
agentcore invoke '{"prompt": "What is the return policy window for opened electronics?", "customer_id": "CUST-123", "session_id": "session-1"}'

```

**Response:**

```json
{
  "response": "Opened electronics can be returned within 15 days from the delivery date in original condition with all accessories.\n"
}

```

---

### Scenario 4: Cross-Session Long-Term Memory

**Turn A (Session A — Preference Storage):**

```bash
agentcore invoke '{"prompt": "My preferred contact method is email and my primary device is an Echo Dot.", "customer_id": "CUST-999", "session_id": "session-A"}'

```

**Response:**

```json
{
  "response": "Thank you! I have saved your preferred contact method as email and your primary device as an Echo Dot.\n"
}

```

**Turn B (Session B — Preference Recall):**

```bash
agentcore invoke '{"prompt": "What is my preferred contact method and primary device?", "customer_id": "CUST-999", "session_id": "session-B"}'

```

**Response:**

```json
{
  "response": "Based on your saved profile preferences, your preferred contact method is email and your primary device is an Echo Dot.\n"
}

```

---

### Scenario 5: Loyalty Discount Calculation

```bash
agentcore invoke '{"prompt": "Calculate my loyalty discount for an order total of $150.00. I am Gold tier with 4250 loyalty points.", "customer_id": "CUST-123", "session_id": "session-1"}'

```

**Response:**

```json
{
  "response": "Your loyalty discount for an order total of $150.00 is as follows:\n- Points Redeemed: 4000\n- Tier Discount: 10%\n- Final Total: $99.00\n- Total Savings: $51.00\n- Points Earned: 99\n- Remaining Points: 349\n\nIf you have any more questions or need further assistance, feel free to ask!\n"
}

```

---

### Scenario 6: Browser Tool Execution

```bash
agentcore invoke '{"prompt": "Use the browser tool to visit [https://aws.amazon.com/bedrock/](https://aws.amazon.com/bedrock/) and tell me what the page says about foundation models.", "customer_id": "CUST-123", "session_id": "session-1"}'

```

**Response:**

```json
{
  "response": "The AWS Bedrock page states that Amazon Bedrock provides managed access to foundation models including Amazon Nova and Titan, Anthropic Claude, Meta Llama, and Mistral AI through a unified API with security and privacy.\n"
}

```

---

## CloudWatch Monitoring Setup

1. **Log Group**: `/aws/bedrock-agentcore/runtimes/CustomerSupportAgent_MyAgent-KsFUR2DGUs-DEFAULT`
2. **Metric Filter**:
* Filter Pattern: `[..., msg = "*ERROR*", ...]` or `"ERROR"`
* Metric Namespace: `AgentCore/Monitoring`
* Metric Name: `RuntimeErrorCount`


3. **CloudWatch Alarm**:
* Condition: `RuntimeErrorCount >= 5` within a 5-minute evaluation period.
* Action: Alerts DevOps team via Amazon SNS.



---

## Written Reflection

### 1. Key Design Decision

During deployment, the agent architecture was designed around **lazy evaluation of runtime dependencies**. The AgentCore microVM enforces a strict 30-second initialization limit. Rather than initiating persistent network handshakes to external MCP Gateways and browser drivers during container boot, external client connections are created just-in-time during the invocation lifecycle. This reduced cold-start time from over 30 seconds down to under 2 seconds.

### 2. Challenge Encountered and Resolution

When invoking the foundational model via the ConverseStream API, Amazon Nova models initially threw an `EventStreamError: Model produced invalid sequence as part of ToolUse` because MCP schema metadata contained non-standard tool payloads. The issue was solved by structuring local `@tool` signatures with rigid typing, implementing explicit fallback routines, and handling the Strands message block format within `MemoryHook` so unformatted JSON payloads never corrupt conversational token streams.

### 3. Future Production Extensions

In a production deployment, this architecture would be extended with:

* **Mutual TLS & IAM SigV4 Authentication**: Replacing the `NONE` authorizer on the AgentCore Gateway with IAM SigV4 signatures to secure tool execution end-to-end.
* **Dynamic Caching Layer**: Integrating Amazon ElastiCache (Redis) in front of the Bedrock Knowledge Base to cache frequently queried return policies and reduce Bedrock runtime token costs.
* **Dead-Letter Queues (DLQ) & Human Escalation**: Adding an automated fallback tool that routes unrecognized or emotionally charged interactions directly to Amazon Connect for human representative handoff.

```

```
