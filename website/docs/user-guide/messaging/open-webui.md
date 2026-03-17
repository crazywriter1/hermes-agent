---
sidebar_position: 14
title: "Open WebUI"
description: "Use Hermes Agent with Open WebUI"
---

# Open WebUI

Hermes Agent can be used with [Open WebUI](https://github.com/open-webui/open-webui), an open-source LLM chat UI that supports local and remote models.

## Architecture

Open WebUI talks to Hermes via the OpenAI-compatible API. A typical flow:

```
+-----------------------------------------------------------------------------+
|  User (browser)  -->  Open WebUI  -->  Hermes API  -->  LLM / tools          |
+-----------------------------------------------------------------------------+
```

Ensure the API base URL in Open WebUI points at your Hermes API server.

## Configuration

1. Run Hermes with the API server enabled (see [API server](/docs/user-guide/features/api-server)).
2. In Open WebUI, set the OpenAI API base URL to your Hermes endpoint (e.g. `http://localhost:8765/v1`).
3. Use any model name; Hermes will handle routing.

## Session behavior

Each Open WebUI conversation uses its own Hermes session. Sessions are keyed by Open WebUI conversation ID so context is preserved per chat.
