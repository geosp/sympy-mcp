<div align="center">
  <img src=".github/logo.png" alt="Sympy MCP Logo" width="400" />
</div>

# Symbolic Algebra MCP Server

Sympy-MCP is a Model Context Protocol server for allowing LLMs to autonomously perform symbolic mathematics and computer algebra. It exposes numerous tools from SymPy's core functionality to MCP clients for manipulating mathematical expressions and equations.

## Why?

Language models are absolutely abysmal at symbolic manipulation. They hallucinate variables, make up random constants, permute terms and generally make a mess. But we have computer algebra systems specifically built for symbolic manipulation, so we can use tool-calling to orchestrate a sequence of transforms so that the symbolic kernel does all the heavy lifting.

While you can certainly have an LLM generate Mathematica or Python code, if you want to use the LLM as an agent or on-the-fly calculator, it's a better experience to use the MCP server and expose the symbolic tools directly.

The server exposes a subset of symbolic mathematics capabilities including algebraic equation solving, integration and differentiation, vector calculus, tensor calculus for general relativity, and both ordinary and partial differential equations.

For example, you can ask it in natural language to solve a differential equation:

> Solve the damped harmonic oscillator with forcing term: the mass-spring-damper system described by the differential equation where m is mass, c is the damping coefficient, k is the spring constant, and F(t) is an external force.

$$ m\frac{d^2x}{dt^2} + c\frac{dx}{dt} + kx = F(t) $$

Or involving general relativity:

> Compute the trace of the Ricci tensor $R_{\mu\nu}$ using the inverse metric $g^{\mu\nu}$ for Anti-de Sitter spacetime to determine its constant scalar curvature $R$.

## Usage

You need [uv](https://docs.astral.sh/uv/getting-started/installation/) first.

- **Homebrew** : `brew install uv`
- **Curl** : `curl -LsSf https://astral.sh/uv/install.sh | sh`

Then clone and install:

```shell
git clone https://github.com/geosp/sympy-mcp.git
cd sympy-mcp
uv sync
```

The server is built on [mcp-service-kit](https://github.com/geosp/mcp-service-kit) and has two run modes:

```shell
# stdio transport — for Claude Desktop, Cursor, and other subprocess-based clients
uv run sympy-mcp --mode stdio

# MCP HTTP server — streamable-HTTP transport, listens on :8081/mcp
uv run sympy-mcp --mode http --port 8081
```

Run `uv run sympy-mcp --help` for all options (`--host`, `--port`, `--log-level`). Settings can also come from environment variables or a `.env` file: `MCP_TRANSPORT`, `MCP_HOST` (default `0.0.0.0`, all interfaces), `MCP_PORT` (default `8081`), `SYMPY_SESSION_TTL` (session lifetime in seconds, default `1800`), and `SYMPY_TIMEOUT` (time limit per computation in seconds, default `30`, `0` for none).

Integration, simplification and ODE solving can run for a very long time on some inputs. Each computing tool therefore runs under a time limit and returns a timeout error instead of blocking the server; a call can override the limit with `timeout_seconds`. The limit uses `SIGALRM`, so it is enforced on Linux and macOS but not on Windows.

## Available Tools

The sympy-mcp server provides the following tools for symbolic mathematics.

Every computing tool stores its result in the session and returns JSON: `{"key": "expr_3", "result": "x**2 - 1", "latex": "x^{2} - 1"}`. Pass `key` to later calls (`expr_key`, `matrix_key`, …) or reference it as `@expr_3` inside any expression string, e.g. `introduce_expression("@expr_3 - @expr_5")`. Failures return `{"error": "..."}`. Pass `output_format="legacy"` to get the plain-string return values from earlier versions.

Expression strings also know SymPy's units (`meter`, `second`, `kelvin`, …) and these physical constants: `speed_of_light`, `gravitational_constant`, `planck`, `hbar`, `boltzmann_constant`, `elementary_charge`, `electron_rest_mass`, `vacuum_permittivity`, `avogadro_number`, `planck_length`. Short aliases such as `c` or `k_B` are not defined, so they stay ordinary symbols.

| Tool | Tool ID | Description |
|------|-------|-------------|
| Variable Introduction | `intro` | Introduces a variable with specified assumptions and stores it |
| Multiple Variables | `intro_many` | Introduces multiple variables with specified assumptions simultaneously |
| Expression Parser | `introduce_expression` | Parses an expression string using available local variables and stores it |
| Equation Parser | `introduce_equation` | Parses and stores an equation (lhs = rhs) |
| LaTeX Printer | `print_latex_expression` | Prints a stored expression in LaTeX format, along with variable assumptions |
| Substitution | `substitute_expression` | Substitutes a variable with an expression in another expression |
| Factorer | `factor_expression` | Factors an expression into irreducible components |
| Expander | `expand_expression` | Expands a product or power into a sum of terms |
| Collector | `collect_expression` | Collects and groups terms by powers of a variable |
| Partial Fractions | `apart_expression` | Decomposes a rational expression into partial fractions |
| Numeric Evaluator | `evalf_expression` | Numerically evaluates an expression to n significant digits |
| Rewriter | `rewrite_expression` | Rewrites an expression in terms of another function (e.g. exp) |
| Log Expander | `expand_log_expression` | Expands logarithms of products and powers (optionally forced) |
| Trig Simplifier | `trigsimp_expression` | Simplifies with trigonometric identities |
| Power Combiner | `powsimp_expression` | Combines powers with the same base or exponent |
| Closed-Form Finder | `nsimplify_expression` | Finds a simple exact expression for a floating-point number |
| Multi-Substitution | `substitute_values` | Substitutes several symbols at once (simultaneously) |
| Simplifier | `simplify_expression` | Simplifies a mathematical expression using SymPy's canonicalize function |
| Equivalence Checker | `check_equivalence` | Decides whether two expressions are equal: symbolic proof first, then numeric spot checks that respect symbol assumptions; returns proved_equal, numerically_equal or not_equal (with a counterexample) |
| Integration | `integrate_expression` | Integrates an expression with respect to a variable |
| Differentiation | `differentiate_expression` | Differentiates an expression with respect to a variable |
| Limit | `limit_expression` | Computes the limit of an expression as a variable approaches a point |
| Series Expansion | `series_expansion` | Computes the Taylor/Maclaurin series expansion of an expression |
| Summation | `summation_expression` | Computes a symbolic summation over a variable range |
| Fourier Transform | `fourier_transform` | Fourier transform, F(k) = ∫ f(x) e^{-2πixk} dx |
| Inverse Fourier | `inverse_fourier_transform` | Inverse Fourier transform (same convention) |
| Laplace Transform | `laplace_transform` | Laplace transform with its convergence abscissa |
| Inverse Laplace | `inverse_laplace_transform` | Inverse Laplace transform |
| Numeric Integration | `numeric_integrate` | Definite integral by mpmath quadrature at chosen precision, infinite limits allowed |
| Algebraic Solver | `solve_algebraically` | Solves an equation algebraically for a given variable over a given domain |
| Linear Solver | `solve_linear_system` | Solves a system of linear equations |
| Nonlinear Solver | `solve_nonlinear_system` | Solves a system of nonlinear equations |
| Function Variable | `introduce_function` | Introduces a function variable for use in differential equations |
| ODE Solver | `dsolve_ode` | Solves an ordinary differential equation, optionally with initial conditions; stores the solution and its right-hand side |
| Coupled ODE Solver | `dsolve_system` | Solves a coupled system of ordinary differential equations, optionally with initial conditions |
| ODE Solution Check | `verify_ode_solution` | Checks that a solution satisfies an ODE or ODE system (`checkodesol`) |
| PDE Solver | `pdsolve_pde` | Solves a partial differential equation |
| Matrix Creator | `create_matrix` | Creates a SymPy matrix from the provided data |
| Determinant | `matrix_determinant` | Calculates the determinant of a matrix |
| Matrix Inverse | `matrix_inverse` | Calculates the inverse of a matrix |
| Eigenvalues | `matrix_eigenvalues` | Calculates the eigenvalues of a matrix |
| Eigenvectors | `matrix_eigenvectors` | Calculates the eigenvectors of a matrix |
| Matrix Product | `matrix_multiply` | Multiplies two stored matrices |
| Matrix Power | `matrix_power` | Raises a square matrix to a (possibly symbolic) power |
| Matrix Exponential | `matrix_exp` | Computes exp(A) |
| Trace | `matrix_trace` | Trace of a square matrix |
| Transpose | `matrix_transpose` | Transpose of a matrix |
| Hermitian Adjoint | `matrix_adjoint` | Conjugate transpose A† |
| Matrix Commutator | `matrix_commutator` | AB − BA for two square matrices |
| Rank | `matrix_rank` | Rank of a matrix |
| Nullspace | `matrix_nullspace` | Basis of the nullspace |
| Boson Operator | `introduce_boson_operator` | Introduces a bosonic annihilation operator a (creation operator Dagger(a)) |
| Normal Ordering | `normal_order_expression` | Normal-orders an operator expression, as the :X: symbol or using [a, a†] = 1 |
| Operator Commutator | `evaluate_commutator` | Evaluates [A, B] for ladder-operator expressions |
| Apply Operators | `quantum_apply` | Applies operators to kets and bras (qapply) |
| Coherent Expectation | `coherent_state_expectation` | ⟨α\|X\|α⟩ for a coherent state, via normal ordering |
| Unit Converter | `convert_to_units` | Converts a quantity to given target units |
| Unit Simplifier | `quantity_simplify_units` | Simplifies a quantity with units |
| Coordinates | `create_coordinate_system` | Creates a 3D coordinate system for vector calculus operations |
| Vector Field | `create_vector_field` | Creates a vector field in the specified coordinate system |
| Curl | `calculate_curl` | Calculates the curl of a vector field |
| Divergence | `calculate_divergence` | Calculates the divergence of a vector field |
| Gradient | `calculate_gradient` | Calculates the gradient of a scalar field |
| Standard Metric | `create_predefined_metric` | Creates a predefined spacetime metric (e.g. Schwarzschild, Kerr, Minkowski) |
| Metric Search | `search_predefined_metrics` | Searches available predefined metrics |
| Tensor Calculator | `calculate_tensor` | Calculates tensors from a metric (Christoffel symbols, Riemann, Ricci, Schouten, Einstein, Weyl tensors) |
| Custom Metric | `create_custom_metric` | Creates a custom metric tensor from provided components and symbols |
| Tensor LaTeX | `print_latex_tensor` | Prints a stored tensor expression in LaTeX format |
| Tensor Creator | `create_tensor` | Creates a vector or tensor field from components in a stored metric's coordinates |
| Covariant Derivative | `covariant_derivative` | Covariant derivative of a stored tensor (derivative index appended last) |
| Tensor Divergence | `tensor_divergence` | Divergence on one index, e.g. ∇^a G_ab, raising the index if needed |
| Index Contraction | `contract_indices` | Contracts two indices of a stored tensor (traces, scalars) |
| Raise Index | `raise_index` | Raises one index with the inverse metric |
| Lower Index | `lower_index` | Lowers one index with the metric |
| Tensor Component | `tensor_component` | Stores one component (by position or coordinate name) as an expression |
| Kretschmann Scalar | `kretschmann_scalar` | Computes R_abcd R^abcd for a stored metric |
| Killing Equation | `killing_equation` | Evaluates ∇_(a ξ_b) for a vector field and reports whether it is a Killing vector |
| Session Creator | `create_session` | Creates a new isolated session and returns a unique session_id |
| Session Lister | `list_sessions` | Lists all active sessions with their descriptions and timestamps |
| Session Reset | `reset_state` | Clears all expressions, symbols, and functions from the session |
| Session Inspector | `list_session_state` | Lists all stored keys in the session grouped by category |
| Key Deletion | `delete_stored_key` | Deletes a stored item by key, searching all stores |
| Session Export | `export_session` | Exports the session's tool calls as a replay script that checks every result, or as a JSON transcript |

By default variables are predefined with assumptions (similar to how the [symbols()](https://docs.sympy.org/latest/modules/core.html#sympy.core.symbol.symbols) function works in SymPy). Unless otherwise specified the default assumptions is that a variable is complex, commutative, a term over the complex field $\mathbb{C}$.

| Property | Value |
|----------|-------|
| `commutative` | true |
| `complex` | true |
| `finite` | true |
| `infinite` | false |

## Claude Desktop Setup

Add the following to your `claude_desktop_config.json`, replacing `/ABSOLUTE_PATH_TO_SYMPY_MCP` with the path to the cloned repo:

* macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
* Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sympy-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE_PATH_TO_SYMPY_MCP",
        "run",
        "sympy-mcp",
        "--mode",
        "stdio"
      ]
    }
  }
}
```

## Cursor Setup

In your `~/.cursor/mcp.json`, add the following:

```json
{
  "mcpServers": {
    "sympy-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE_PATH_TO_SYMPY_MCP",
        "run",
        "sympy-mcp",
        "--mode",
        "stdio"
      ]
    }
  }
}
```

## VS Code Setup

VS Code and VS Code Insiders now support MCPs in [agent mode](https://code.visualstudio.com/blogs/2025/04/07/agentMode). For VS Code, you may need to enable `Chat > Agent: Enable` in the settings.

1. **One-click Setup:**

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=sympy-mcp&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22ghcr.io%2Fgeosp%2Fsympy-mcp%3Alatest%22%2C%22uv%22%2C%22run%22%2C%22sympy-mcp%22%2C%22--mode%22%2C%22stdio%22%5D%7D)

[![Install in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-Install_Server-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=sympy-mcp&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22ghcr.io%2Fgeosp%2Fsympy-mcp%3Alatest%22%2C%22uv%22%2C%22run%22%2C%22sympy-mcp%22%2C%22--mode%22%2C%22stdio%22%5D%7D&quality=insiders)

OR manually add to your `settings.json` (global):

```json
{
  "mcp": {
    "servers": {
      "sympy-mcp": {
        "command": "uv",
        "args": [
          "--directory",
          "/ABSOLUTE_PATH_TO_SYMPY_MCP",
          "run",
          "sympy-mcp",
          "--mode",
          "stdio"
        ]
      }
    }
  }
}
```

2. Click "Start" above the server config, switch to agent mode in the chat, and try commands like "integrate x^2" or "solve x^2 = 1" to get started.

## Cline Setup

To use with [Cline](https://cline.bot/), first start the MCP HTTP server:

```shell
uv run sympy-mcp --mode http --port 8081
```

Then open Cline, select "MCP Servers" → "Remote Servers" and add:

- Server Name: `sympy-mcp`
- Server URL: `http://127.0.0.1:8081/mcp`

## 5ire Setup

Another MCP client that supports multiple models (o3, o4-mini, DeepSeek-R1, etc.) on the backend is 5ire.

To set up with [5ire](https://github.com/nanbingxyz/5ire), open 5ire and go to Tools -> New and set the following configurations:

- Tool Key: `sympy-mcp`
- Name: SymPy MCP
- Command: `/opt/homebrew/bin/uv --directory /ABSOLUTE_PATH_TO_SYMPY_MCP run sympy-mcp --mode stdio`

Replace `/ABSOLUTE_PATH_TO_SYMPY_MCP` with the actual path to the cloned repo.

## HTTP Transport (Streamable HTTP)

The server supports MCP over HTTP using the [streamable-HTTP transport](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http) introduced in MCP spec 2025-03-26. This exposes a single `/mcp` endpoint that clients connect to over HTTP.

This is the recommended transport when running the server as a standalone process or in a container, because it allows any HTTP-capable MCP client to connect without needing to launch the server as a subprocess.

```bash
# Run MCP HTTP server locally
uv run sympy-mcp --mode http --port 8081
```

The server has no built-in authentication. Put it behind a gateway if it needs to be reachable beyond localhost. HTTP mode runs with authentication disabled by default (`MCP_AUTH_ENABLED=false`) and logs a warning saying so; setting `MCP_AUTH_ENABLED=true` makes it refuse to start, since there is no auth provider to enforce it.

A `/health` endpoint is exposed in HTTP mode, returning:

```json
{"status": "ok", "service": "sympy", "active_sessions": 0}
```

## Security

Expression strings are parsed by SymPy, which evaluates them as Python. The server restricts that evaluation (`sympy_mcp/parsing.py`):

- **Restricted namespace.** Only SymPy's names are available: no Python builtins (`open`, `eval`, `__import__`, …), no modules, and none of SymPy's helpers that generate or evaluate code (`sympify`, `lambdify`, `nsolve`, `parse_expr`, plotting, …).
- **Input checks.** Input is limited to 10,000 characters and may not contain `__`.
- **Checks on the transformed code.** It may not contain lambdas, comprehensions, attributes starting with `_`, or frame and code introspection attributes such as `gi_frame` and `f_globals`. Quoted strings are allowed only as names, e.g. `Symbol('x')`.
- **Strings built at runtime.** A string that SymPy parses during an expression, e.g. via `sin(<string>)`, goes through the same restrictions. A parse result may not contain strings.

These checks close the known routes from an expression to arbitrary code, and tests cover them (`tests/test_safe_parsing.py`). But an in-process `eval` can't be proven to be a complete sandbox. Run the server with least privilege, e.g. in the provided container without secrets or write access to anything important, and put authentication in front of any HTTP deployment that others can reach.

## Running in Container

You can build and run the server using Docker locally:

```bash
# Build the Docker image
docker build -t sympy-mcp .

# Run as MCP HTTP server (port 8081, /mcp endpoint) — the image's default command
docker run -p 8081:8081 sympy-mcp
```

Or use Docker Compose from the `docker/` directory:

```bash
cd docker
docker compose up -d --build
```

This starts `sympy-mcp`, the MCP HTTP server, on **port 8082** (`/mcp` endpoint).

Alternatively, pull the pre-built image from GitHub Container Registry:

```bash
docker pull ghcr.io/geosp/sympy-mcp:latest
docker run -p 8081:8081 --rm ghcr.io/geosp/sympy-mcp:latest
```

To configure Claude Desktop to launch the Docker container directly:

```json
{
  "mcpServers": {
    "sympy-mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "sympy-mcp",
        "uv", "run", "sympy-mcp", "--mode", "stdio"
      ]
    }
  }
}
```

## Example Interaction 1 : Differential Equations

Here's an example of how the tool-calling works in a conversation with an AI assistant using this MCP server:

**User**: Solve the damped harmonic oscillator with forcing term: the mass-spring-damper system described by the differential equation where m is mass, c is the damping coefficient, k is the spring constant, and F(t) is an external force.

$$ m\frac{d^2x}{dt^2} + c\frac{dx}{dt} + kx = F(t) $$

**Assistant**: (Internal tool call) `create_session` to start a session:
```json
{
  "description": "damped harmonic oscillator"
}
```

**Assistant**: (Internal tool call) `intro_many` to introduce variables:
```json
{
  "session_id": "<session_id>",
  "variables": [
    {"var_name": "t", "assumptions": ["real"], "negative_assumptions": []},
    {"var_name": "m", "assumptions": ["real", "positive"], "negative_assumptions": []},
    {"var_name": "c", "assumptions": ["real", "positive"], "negative_assumptions": []},
    {"var_name": "k", "assumptions": ["real", "positive"], "negative_assumptions": []}
  ]
}
```

**Assistant**: (Internal tool call) `introduce_function` to define x(t):
```json
{
  "session_id": "<session_id>",
  "func_name": "x"
}
```

**Assistant**: (Internal tool call) `introduce_expression` to create the differential equation:
```json
{
  "session_id": "<session_id>",
  "expression": "Eq(m*Derivative(x(t), t, t) + c*Derivative(x(t), t) + k*x(t), F(t))"
}
```

**Assistant**: (Internal tool call) `print_latex_expression` to display the equation nicely:
```json
{
  "session_id": "<session_id>",
  "expr_key": "expr_12"
}
```

Result:

$$
c \frac{d}{d t} x{\left(t \right)} + k x{\left(t \right)} + m \frac{d^{2}}{d t^{2}} x{\left(t \right)} = F{\left(t \right)}
$$

**Assistant**: (Internal tool call) `introduce_function` to define F(t):
```json
{
  "session_id": "<session_id>",
  "func_name": "F"
}
```

**Assistant**: (Internal tool call) `dsolve_ode` to solve the differential equation:
```json
{
  "session_id": "<session_id>",
  "expr_key": "expr_12",
  "func_name": "x"
}
```

Result:

$$
x{\left(t \right)} = C_{1} e^{\frac{t \left(- c + \sqrt{c^{2} - 4 k m}\right)}{2 m}} + C_{2} e^{- \frac{t \left(c + \sqrt{c^{2} - 4 k m}\right)}{2 m}} + \cdots
$$

## Example Interaction 2: General Relativity

**User**: Compute the trace of the Ricci tensor $R_{\mu\nu}$ using the inverse metric $g^{\mu\nu}$ for Anti-de Sitter spacetime to determine its constant scalar curvature $R$.

**Assistant**: (Internal tool call) `create_session` to start a session:
```json
{
  "description": "Anti-de Sitter Ricci scalar"
}
```

**Assistant**: (Internal tool call) `create_predefined_metric` to create the Anti-de Sitter metric:
```json
{
  "session_id": "<session_id>",
  "metric_name": "AntiDeSitter"
}
```

**Assistant**: (Internal tool call) `calculate_tensor` to calculate the Ricci tensor:
```json
{
  "session_id": "<session_id>",
  "metric_key": "metric_AntiDeSitter",
  "tensor_type": "RICCI_TENSOR",
  "simplify": true
}
```

**Assistant**: (Internal tool call) `print_latex_tensor` to display the Ricci tensor:
```json
{
  "session_id": "<session_id>",
  "tensor_key": "riccitensor_metric_AntiDeSitter"
}
```

Result:

$$
\left[\begin{matrix}3 & 0 & 0 & 0\\\\0 & - 3 \cos^{2}{\left(t \right)} & 0 & 0\\\\0 & 0 & - 3 \cos^{2}{\left(t \right)} \sinh^{2}{\left(\chi \right)} & 0\\\\0 & 0 & 0 & - 3 \sin^{2}{\left(\theta \right)} \cos^{2}{\left(t \right)} \sinh^{2}{\left(\chi \right)}\end{matrix}\right]
$$

**Assistant**: (Internal tool call) `calculate_tensor` to calculate the Ricci scalar:
```json
{
  "session_id": "<session_id>",
  "metric_key": "metric_AntiDeSitter",
  "tensor_type": "RICCI_SCALAR",
  "simplify": true
}
```

**Assistant**: (Internal tool call) `print_latex_tensor` to display the Ricci scalar:
```json
{
  "session_id": "<session_id>",
  "tensor_key": "ricciscalar_metric_AntiDeSitter"
}
```

Result:

$$
-12
$$

## Example Interaction 3: Coupled ODE System (Fluid Dynamics)

This example demonstrates solving a coupled system of ODEs and verifying the solution against an algebraic steady-state analysis — a task where LLMs typically hallucinate without a CAS to ground each step.

**User**:

> Use the sympy-mcp tools to solve this symbolically — do not compute by hand.
>
> Two cylindrical tanks are connected by a pipe. Tank 1 has cross-sectional area A₁ = 2 m² and receives a constant inflow of Q = 0.5 m³/s. Water drains from Tank 1 into Tank 2 through a pipe with flow rate proportional to the height difference: q₁₂ = k·(h₁ - h₂) where k = 0.3 m²/s. Tank 2 has cross-sectional area A₂ = 1 m² and drains to the outside at rate q₂ = k·h₂ with the same k.
>
> Set up and solve the coupled system of ODEs for the water heights h₁(t) and h₂(t), starting from empty tanks (h₁(0) = 0, h₂(0) = 0). Then find the steady-state heights as t → ∞ by solving the equilibrium equations algebraically, and verify they match the long-term solution of the ODEs.

**Assistant**: (Internal tool chain)

1. `intro_many` — introduce `t`, `k`, `A1`, `A2`, `Q` with real/positive assumptions
2. `introduce_function` × 2 — introduce `h1(t)` and `h2(t)` as unknown functions
3. `introduce_expression` × 2 — encode the mass-balance ODEs:

$$A_1 \frac{dh_1}{dt} = Q - k(h_1 - h_2), \quad A_2 \frac{dh_2}{dt} = k(h_1 - h_2) - k h_2$$

4. `substitute_expression` — substitute numeric values for `k`, `A1`, `A2`, `Q`
5. `dsolve_system` — solve the coupled system directly; apply initial conditions via `substitute_expression`
6. `introduce_expression` × 2 — encode equilibrium equations (derivatives set to zero)
7. `solve_linear_system` — solve the 2×2 algebraic system for `h1*`, `h2*`
8. `print_latex_expression` — display both the time-domain solution and the steady-state values

## Security Disclaimer

This server runs on your computer and gives the language model access to run Python logic. Notably it uses Sympy's `parse_expr` to parse mathematical expressions, which uses `eval` under the hood, effectively allowing arbitrary code execution. By running the server, you are trusting the code that Claude generates. Running in the Docker image is slightly safer, but it's still a good idea to review the code before running it.


## Contributors

- [Stephen Diehl](https://github.com/sdiehl) — original author
- [Geovanny Fajardo](https://github.com/geosp) — new MCP architecture (dual-transport, feature auto-discovery, session management), REST API, Docker deployment, and expanded tool set (algebraic manipulation, calculus completion, state management)

## License

Copyright 2025 Stephen Diehl.

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
