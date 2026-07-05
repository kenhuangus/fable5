# Data handling policy (excerpt)

1. PII (names, emails, SSNs, phone numbers) must never appear in plaintext
   application logs.
2. Every agent tool call must be logged with a request id, the tool name,
   and a timestamp.
3. Secrets (API keys, tokens, passwords) must never appear in agent output
   sent to an end user.
