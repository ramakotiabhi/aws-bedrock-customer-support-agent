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

markdown



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
| **Execution Role** | `AgentCore-CustomerSupport-ApplicationAgentMyAgentRu-sgoCiekBlTH9` | IAM role attached with project execution access|


<img width="1080" height="759" alt="Screenshot 2026-09-17 154109" src="https://github.com/user-attachments/assets/be896da5-4af6-4f03-9673-2a379840a898" />

<img width="1137" height="572" alt="Screenshot 2026-09-17 154532" src="https://github.com/user-attachments/assets/1fe5564b-f04b-4b19-9530-6a27809664b7" />

<img width="308" height="459" alt="Screenshot 2026-09-17 150752" src="https://github.com/user-attachments/assets/47acbd8a-0b0f-44a8-a35c-cb8534221739" />


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


```
<img width="1506" height="205" alt="Screenshot 2026-09-21 214956" src="https://github.com/user-attachments/assets/345d7d79-9d87-4444-99a9-a4fb1c00754e" />

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
<img width="1508" height="117" alt="Screenshot 2026-09-21 215055" src="https://github.com/user-attachments/assets/bb052fb0-8e01-4a83-9587-7d47241ce89d" />
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
<img width="1466" height="88" alt="Screenshot 2026-09-22 114711" src="https://github.com/user-attachments/assets/abe3e428-4b46-4b47-a9ff-c7b2dca4fee6" />


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
<img width="717" height="60" alt="Screenshot 2026-09-22 122237" src="https://github.com/user-attachments/assets/d3bba5a1-f591-4412-a15a-2cbd13005941" />


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
<img width="781" height="65" alt="Screenshot 2026-09-22 120846" src="https://github.com/user-attachments/assets/5963a65c-2599-4964-a9f2-d79bf745ba98" />


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
<img width="1510" height="139" alt="Screenshot 2026-09-22 114918" src="https://github.com/user-attachments/assets/6592eec3-42f9-4f53-9bfb-a1d53c20028a" />


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
<img width="1506" height="140" alt="Screenshot 2026-09-22 115010" src="https://github.com/user-attachments/assets/41b1120f-0374-4fd8-9bf4-65ebe21dc10b" />

Gateway Multi-Tool Verification Log: Terminal output showing both order lookup and refund handling executed within the same session.   

<img width="1510" height="126" alt="Screenshot 2026-09-22 115048" src="https://github.com/user-attachments/assets/50fbafd9-2045-4228-869f-860ff9509fd5" />

---

## CloudWatch Monitoring Setup

1. **Log Group**: `/aws/bedrock-agentcore/runtimes/CustomerSupportAgent_MyAgent-KsFUR2DGUs-DEFAULT`
2. **Metric Filter**:
* Filter Pattern: `[..., msg = "*ERROR*", ...]` or `"ERROR"`
* Metric Namespace: `AgentCore/Monitoring`
* Metric Name: `RuntimeErrorCount`

<img width="885" height="708" alt="Screenshot 2026-09-21 223144" src="https://github.com/user-attachments/assets/64779c91-cfc5-49c9-a4b2-b5d0d8a060c4" />

<img width="870" height="797" alt="Screenshot 2026-09-21 223150" src="https://github.com/user-attachments/assets/e18cc26a-b2e7-4001-98cc-e295e3097d31" />

<img width="1049" height="770" alt="Screenshot 2026-09-21 223423" src="https://github.com/user-attachments/assets/3922137d-d572-4aae-8c5e-db23df26cbfd" />
<img width="1228" height="506" alt="Screenshot 2026-09-21 224212" src="https://github.com/user-attachments/assets/a2a16fef-7439-4680-b104-8b58a159854d" />
<img width="1060" height="808" alt="Screenshot 2026-09-21 223912" src="https://github.com/user-attachments/assets/13155c55-3785-4aa3-bea7-9b96131e7ef3" />
<img width="985" height="705" alt="Screenshot 2026-09-21 224220" src="https://github.com/user-attachments/assets/a518b2d5-59dd-4ba0-84eb-cf6ed8623b46" />

<img width="992" height="562" alt="Screenshot 2026-09-21 224230" src="https://github.com/user-attachments/assets/5d5811ba-3861-468c-be5b-c4485ccab4d1" />

3. **CloudWatch Alarm**:
* Condition: `RuntimeErrorCount >= 5` within a 5-minute evaluation period.
* Action: Alerts DevOps team via Amazon SNS.
<img width="545" height="336" alt="Screenshot 2026-09-21 224323" src="https://github.com/user-attachments/assets/65a425d0-1473-4a83-890f-94491dd983bd" />



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
