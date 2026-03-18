# Architecture

## Overview

`sympy-mcp` is built on a dual-transport architecture: the same symbolic math engine is exposed either as an MCP server (for AI clients) or as a REST API (for HTTP clients), both running from the same codebase.

The entrypoint is the `sympy-mcp` CLI (`sympy_mcp/server.py:main`), which selects a transport mode at startup. All symbolic computation happens in `SymPyState` (one instance per session), managed by `SymPySessionManager`.

---

## Transport Modes

```mermaid
flowchart TD
    CLI["sympy-mcp CLI\n--mode stdio|mcp|rest"]

    CLI -->|"stdio"| STDIO["BaseMCPServer\nrun_stdio_transport()\nFastMCP over stdin/stdout"]
    CLI -->|"mcp"| MCP["BaseMCPServer\nrun_mcp_only()\nFastMCP http_app()\n:8081/mcp"]
    CLI -->|"rest"| REST["BaseMCPServer\ncreate_fastapi_app()\nFastAPI + FastMCP mounted\n:8081"]

    STDIO --> SM["SymPySessionManager"]
    MCP --> SM
    REST --> SM

    SM --> STATE["SymPyState\n(one per session_id)"]
```

| Mode | Transport | Endpoint | Use case |
|------|-----------|----------|----------|
| `stdio` | stdin/stdout | — | Claude Desktop, Cursor, subprocess clients |
| `mcp` | HTTP | `:8081/mcp` | Cline, HTTP-capable MCP clients, Docker |
| `rest` | HTTP | `:8081/*` | Direct API access, debugging, custom integrations |

In `stdio` and `mcp` modes (`MCP_ONLY=true`), `BaseMCPServer.run_mcp_only()` runs FastMCP's Starlette app directly — the FastAPI router is **not** mounted. A `/health` custom route is registered on the FastMCP instance via `@mcp.custom_route()` so health checks work in all modes.

In `rest` mode, FastAPI wraps a full router (feature routes + `/health` + session management endpoints).

---

## Feature Module Structure

Each capability area is a Python package under `sympy_mcp/features/`. Every feature follows the same three-file convention:

```
sympy_mcp/features/<feature>/
├── instructions.md # Tool descriptions loaded into MCP docstrings at runtime
├── models.py       # Pydantic request/response models
├── routes.py       # REST routes — create_router(session_manager) → APIRouter
└── tool.py         # MCP tools — register_tool(mcp, session_manager)
```

Both `routes.py` and `tool.py` are **auto-discovered** at startup — no manual registration needed when adding a new feature.

```mermaid
flowchart LR
    subgraph Discovery ["Auto-discovery (startup)"]
        SRV["SymPyMCPServer\ncreate_router()"]
        SVC["SymPyMCPService\nregister_mcp_tools()"]
    end

    subgraph Features ["sympy_mcp/features/"]
        direction TB
        CALC["calculus\ntool.py · routes.py"]
        EXPR["expressions\ntool.py · routes.py"]
        SESS["session\ntool.py · routes.py"]
        SYMS["symbols\ntool.py · routes.py"]
        SOLV["solving\ntool.py · routes.py"]
        LA["linear_algebra\ntool.py · routes.py"]
        FUNC["functions\ntool.py · routes.py"]
        UNITS["units\ntool.py · routes.py"]
        VCALC["vector_calc\ntool.py · routes.py"]
        REL["relativity\ntool.py · routes.py"]
    end

    SRV -- "imports routes.py\ncreate_router()" --> Features
    SVC -- "imports tool.py\nregister_tool()" --> Features
```

### Adding a new feature

1. Create `sympy_mcp/features/<name>/` with `instructions.md`, `models.py`, `routes.py`, `tool.py`
2. Write tool descriptions in `instructions.md` — these are injected as MCP docstrings at runtime
3. Implement `create_router(session_manager) -> APIRouter` in `routes.py`
4. Implement `register_tool(mcp, session_manager)` in `tool.py`
5. Add the computation method to `SymPyState` in `sympy_mcp/state.py`

Both `routes.py` and `tool.py` **must** be updated — they are independent registrations.

---

## Request Flow

### MCP tool call (stdio or HTTP)

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant FastMCP
    participant Tool as tool.py
    participant SM as SymPySessionManager
    participant State as SymPyState

    Client->>FastMCP: tools/call {name, arguments}
    FastMCP->>Tool: registered async fn(session_id, ...)
    Tool->>SM: get_sync(session_id)
    SM-->>Tool: SymPyState instance
    Tool->>State: state.method(args)
    State-->>Tool: result key or value
    Tool-->>FastMCP: str result
    FastMCP-->>Client: CallToolResult
```

### REST API call

```mermaid
sequenceDiagram
    participant Client as HTTP Client
    participant FastAPI
    participant Route as routes.py
    participant SM as SymPySessionManager
    participant State as SymPyState

    Client->>FastAPI: POST /expressions/factor {session_id, expr_key}
    FastAPI->>Route: route handler(request: FactorRequest)
    Route->>SM: get_sync(session_id)
    SM-->>Route: SymPyState instance
    Route->>State: state.factor_expression(expr_key)
    State-->>Route: raw key (e.g. "expr_3")
    Note over Route: resolve_result(raw) → human-readable string
    Route-->>FastAPI: ExpressionResponse(result=..., result_key=...)
    FastAPI-->>Client: JSON response
```

---

## Session and State Model

Each unique `session_id` maps to a `SessionEntry` (metadata + an isolated `SymPyState` instance). Sessions must be explicitly created via `create_session` (MCP) or `POST /sessions` (REST), which returns a server-generated UUID. Unknown session IDs are rejected with a `SessionNotFoundError`.

`get_sync()` updates `last_accessed` on every call, enabling future TTL-based eviction (configured via `ttl_seconds` at startup, default 1800 s).

```mermaid
flowchart TD
    subgraph Manager ["SymPySessionManager (in-memory)\n_store: Dict[str, SessionEntry]"]
        SE1["session_id: UUID\nSessionEntry\n─────────────\ndescription: str\ncreated_at: datetime\nlast_accessed: datetime"]
        SE2["session_id: UUID\nSessionEntry\n─────────────\ndescription: str\ncreated_at: datetime\nlast_accessed: datetime"]
    end

    subgraph State ["SymPyState (per SessionEntry)"]
        LV["local_vars\n{x: Symbol('x'), ...}"]
        US["user_symbols\n{x: Symbol('x'), ...}"]
        EX["expressions\n{expr_1: x**2, expr_2: 2*x, ...}"]
        FN["functions\n{f: Function('f')}"]
        CS["coordinate_systems\n{R: CoordSys3D}"]
        MT["metrics\n{metric_Schwarzschild: ...}"]
        TO["tensor_objects\n{riccitensor_...: ...}"]
    end

    SE1 -->|".state"| State
```

**Key rules:**
- All tool calls sharing state **must** use the same `session_id` — different IDs are completely isolated namespaces
- Session IDs are server-generated UUIDs — clients cannot choose their own
- `user_symbols` tracks only explicitly introduced symbols (via `intro`/`intro_many`); `local_vars` also includes unit constants loaded at init
- Most computation methods return a **key** (e.g. `"expr_3"`) that is stored in `expressions` — pass this key as `expr_key` in subsequent tool calls
- `get_sync()` (used by all tools) touches `last_accessed`; `get()` (async, returns `None` on miss) is available for non-tool code

---

## Result Key Pattern

Computation tools use a key-based chaining pattern to avoid serializing large symbolic expressions across tool calls:

```mermaid
flowchart LR
    I["introduce_expression\nexpression: 'x**2 - 1'"] -->|"result_key: 'expr_1'"| F
    F["factor_expression\nexpr_key: 'expr_1'"] -->|"result_key: 'expr_2'"| L
    L["print_latex_expression\nexpr_key: 'expr_2'"] -->|"result: '(x-1)(x+1)'"| OUT["Display"]
```

- `result` — human-readable string (for display)
- `result_key` — session storage key (for chaining into the next tool call)

The `series_expansion` tool is a special case: it stores the polynomial (without the big-O term) under the result key, but returns the full series with O() notation in `result` for display.

---

## Docker Compose Services

```mermaid
flowchart LR
    subgraph Host
        P1["Host :8081"]
        P2["Host :8082"]
    end

    subgraph Containers
        REST["sympy-mcp-rest\n--mode rest\nContainer :8081"]
        MCP["sympy-mcp-mcp\n--mode mcp\nContainer :8081"]
    end

    P1 --> REST
    P2 --> MCP

    REST -->|"GET /health"| H1["{'status':'ok'}"]
    MCP -->|"GET /health"| H2["{'status':'ok'}"]
    MCP -->|"POST /mcp"| H3["MCP protocol"]
```

Both containers are built from the same `Dockerfile`. Dependencies are pre-installed at build time via `uv sync --frozen --no-dev`, so startup is instant with no network access required.
