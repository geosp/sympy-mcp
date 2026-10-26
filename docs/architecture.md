# Architecture

## Overview

`sympy-mcp` exposes a symbolic math engine to AI clients over the Model Context Protocol. The server framework comes from [mcp-service-kit](https://github.com/geosp/mcp-service-kit): it provides the stdio and streamable-HTTP transports, the standard CLI, and environment-based configuration.

The entrypoint is the `sympy-mcp` CLI (`sympy_mcp/server.py:main`, built with `create_main_with_modes`), which selects a transport at startup. All symbolic computation happens in `SymPyState` (one instance per session), managed by `SymPySessionManager`.

---

## Transport Modes

```mermaid
flowchart TD
    CLI["sympy-mcp CLI\n--mode stdio|http"]

    CLI -->|"stdio"| STDIO["SymPyMCPServer (BaseMCPServer)\nFastMCP over stdin/stdout"]
    CLI -->|"http"| HTTP["SymPyMCPServer (BaseMCPServer)\nFastMCP streamable HTTP\n:8081/mcp"]

    STDIO --> SM["SymPySessionManager"]
    HTTP --> SM

    SM --> STATE["SymPyState\n(one per session_id)"]
```

| Mode | Transport | Endpoint | Use case |
|------|-----------|----------|----------|
| `stdio` | stdin/stdout | — | Claude Desktop, Cursor, subprocess clients |
| `http` | HTTP | `:8081/mcp` | Cline, HTTP-capable MCP clients, Docker |

A `/health` custom route is registered on the FastMCP instance via `@mcp.custom_route()` (in `sympy_mcp/service.py`), so HTTP deployments can be health-checked.

### Configuration

`sympy_mcp/config.py` defines `AppConfig`, a pydantic-settings model with two sections. The kit's `main()` loads `.env` first, then applies CLI flags on top.

| Section | Class | Environment variables |
|---------|-------|-----------------------|
| `server` | `SymPyServerConfig` (extends the kit's `BaseServerConfig`) | `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT` (default `8081`), `MCP_AUTH_ENABLED` (default `false`) |
| `sympy` | `SymPyConfig` | `SYMPY_SESSION_TTL` (default `1800`) |

The server has no auth provider. Authentication is expected at the gateway in front of it. Setting `MCP_AUTH_ENABLED=true` makes HTTP mode refuse to start (mcp-service-kit ≥ 0.2 fails closed when auth is enabled without a provider), rather than serve without authentication.

---

## Feature Module Structure

Each capability area is a Python package under `sympy_mcp/features/`. Every feature follows the same two-file convention:

```
sympy_mcp/features/<feature>/
├── instructions.md # Tool descriptions loaded into MCP docstrings at runtime
└── tool.py         # MCP tools — register_tool(mcp, session_manager)
```

`tool.py` is **auto-discovered** at startup by `SymPyMCPService.register_mcp_tools()` — no manual registration needed when adding a new feature.

```mermaid
flowchart LR
    SVC["SymPyMCPService\nregister_mcp_tools()"]

    subgraph Features ["sympy_mcp/features/"]
        direction TB
        CALC["calculus"]
        EXPR["expressions"]
        SESS["session"]
        SYMS["symbols"]
        SOLV["solving"]
        LA["linear_algebra"]
        FUNC["functions"]
        UNITS["units"]
        VCALC["vector_calc"]
        REL["relativity"]
    end

    SVC -- "imports tool.py\nregister_tool()" --> Features
```

### Adding a new feature

1. Create `sympy_mcp/features/<name>/` with `__init__.py`, `instructions.md` and `tool.py`
2. Write tool descriptions in `instructions.md` — these are injected as MCP docstrings at runtime
3. Implement `register_tool(mcp, session_manager)` in `tool.py`
4. Add the computation method to `SymPyState` in `sympy_mcp/state.py`

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

---

## Session and State Model

Each unique `session_id` maps to a `SessionEntry` (metadata + an isolated `SymPyState` instance). Sessions must be explicitly created via the `create_session` tool, which returns a server-generated UUID. Unknown session IDs are rejected with a `SessionNotFoundError`.

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

Computation tools use a key-based chaining pattern to avoid serializing large symbolic expressions across tool calls. Every computing tool stores its result and returns `{"key", "result", "latex"}`:

```mermaid
flowchart LR
    I["introduce_expression\nexpression: 'x**2 - 1'"] -->|"key: 'expr_0'"| F
    F["factor_expression\nexpr_key: 'expr_0'"] -->|"key: 'expr_1'"| C
    C["check_equivalence\nexpr_a: '@expr_1'\nexpr_b: '(x-1)*(x+1)'"] -->|"verdict: proved_equal"| OUT["Display"]
```

- `key` — session storage key, for chaining into the next tool call or for `@key` references inside expression strings
- `result` — the stored value as a SymPy string
- `latex` — the stored value in LaTeX

Internally, `SymPyState` computing methods return a `StoredResult` (`sympy_mcp/results.py`): a `str` equal to the tool's legacy return value that also carries the key and value. The tool wrapper renders it with `format_output()` according to `output_format` (`"structured"` by default, or `"legacy"`).

The `series_expansion` tool stores the polynomial without the big-O term under `key`, and adds the full series with O() notation as `series` / `series_latex` for display.

---

## Transcripts and Export

`SymPyMCPServer.create_middleware()` installs `TranscriptMiddleware` (`sympy_mcp/transcript.py`). For every tool call that names a `session_id`, it appends `{tool, arguments, result}` (or `error`) to that session's `SymPyState.transcript`. The session bookkeeping tools are not recorded. `export_session` renders the transcript as JSON, or as a Python script that replays the calls against a fresh in-process server and compares every result with the recorded one.

---

## Docker Compose Service

```mermaid
flowchart LR
    P["Host :8082"] --> MCP["sympy-mcp\n--mode http\nContainer :8081"]

    MCP -->|"GET /health"| H1["{'status':'ok'}"]
    MCP -->|"POST /mcp"| H2["MCP protocol"]
```

The container is built from the `Dockerfile`. Dependencies are pre-installed at build time via `uv sync --frozen --no-dev`, so startup is instant with no network access required.
