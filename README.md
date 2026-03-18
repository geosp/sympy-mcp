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
git clone https://github.com/sdiehl/sympy-mcp.git
cd sympy-mcp
uv sync
```

The server has three run modes:

```shell
# stdio transport — for Claude Desktop, Cursor, and other subprocess-based clients
uv run sympy-mcp --mode stdio

# MCP HTTP server — streamable-HTTP transport, listens on :8081/mcp
uv run sympy-mcp --mode mcp --port 8081

# REST API — direct HTTP access for testing and custom integrations
uv run sympy-mcp --mode rest --port 8081
```

## Available Tools

The sympy-mcp server provides the following tools for symbolic mathematics:

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
| Simplifier | `simplify_expression` | Simplifies a mathematical expression using SymPy's canonicalize function |
| Integration | `integrate_expression` | Integrates an expression with respect to a variable |
| Differentiation | `differentiate_expression` | Differentiates an expression with respect to a variable |
| Limit | `limit_expression` | Computes the limit of an expression as a variable approaches a point |
| Series Expansion | `series_expansion` | Computes the Taylor/Maclaurin series expansion of an expression |
| Summation | `summation_expression` | Computes a symbolic summation over a variable range |
| Algebraic Solver | `solve_algebraically` | Solves an equation algebraically for a given variable over a given domain |
| Linear Solver | `solve_linear_system` | Solves a system of linear equations |
| Nonlinear Solver | `solve_nonlinear_system` | Solves a system of nonlinear equations |
| Function Variable | `introduce_function` | Introduces a function variable for use in differential equations |
| ODE Solver | `dsolve_ode` | Solves an ordinary differential equation |
| PDE Solver | `pdsolve_pde` | Solves a partial differential equation |
| Matrix Creator | `create_matrix` | Creates a SymPy matrix from the provided data |
| Determinant | `matrix_determinant` | Calculates the determinant of a matrix |
| Matrix Inverse | `matrix_inverse` | Calculates the inverse of a matrix |
| Eigenvalues | `matrix_eigenvalues` | Calculates the eigenvalues of a matrix |
| Eigenvectors | `matrix_eigenvectors` | Calculates the eigenvectors of a matrix |
| Unit Converter | `convert_to_units` | Converts a quantity to given target units |
| Unit Simplifier | `quantity_simplify_units` | Simplifies a quantity with units |
| Coordinates | `create_coordinate_system` | Creates a 3D coordinate system for vector calculus operations |
| Vector Field | `create_vector_field` | Creates a vector field in the specified coordinate system |
| Curl | `calculate_curl` | Calculates the curl of a vector field |
| Divergence | `calculate_divergence` | Calculates the divergence of a vector field |
| Gradient | `calculate_gradient` | Calculates the gradient of a scalar field |
| Standard Metric | `create_predefined_metric` | Creates a predefined spacetime metric (e.g. Schwarzschild, Kerr, Minkowski) |
| Metric Search | `search_predefined_metrics` | Searches available predefined metrics |
| Tensor Calculator | `calculate_tensor` | Calculates tensors from a metric (Ricci, Einstein, Weyl tensors) |
| Custom Metric | `create_custom_metric` | Creates a custom metric tensor from provided components and symbols |
| Tensor LaTeX | `print_latex_tensor` | Prints a stored tensor expression in LaTeX format |
| Session Reset | `reset_state` | Clears all expressions, symbols, and functions from the session |
| Session Inspector | `list_session_state` | Lists all stored keys in the session grouped by category |
| Key Deletion | `delete_stored_key` | Deletes a stored item by key, searching all stores |

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

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=sympy-mcp&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22-p%22%2C%228081%3A8081%22%2C%22--rm%22%2C%22ghcr.io%2Fsdiehl%2Fsympy-mcp%3Amain%22%5D%7D)

[![Install in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-Install_Server-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=sympy-mcp&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22-p%22%2C%228081%3A8081%22%2C%22--rm%22%2C%22ghcr.io%2Fsdiehl%2Fsympy-mcp%3Amain%22%5D%7D&quality=insiders)

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
uv run sympy-mcp --mode mcp --port 8081 --no-auth
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
uv run sympy-mcp --mode mcp --port 8081 --no-auth

# Run REST API locally (useful for debugging and custom integrations)
uv run sympy-mcp --mode rest --port 8081 --no-auth
```

A `/health` endpoint is exposed in both modes, returning:

```json
{"status": "ok", "service": "sympy", "active_sessions": 0}
```

## Running in Container

You can build and run the server using Docker locally:

```bash
# Build the Docker image
docker build -t sympy-mcp .

# Run as MCP HTTP server (port 8081, /mcp endpoint)
docker run -p 8081:8081 sympy-mcp uv run sympy-mcp --mode mcp --host 0.0.0.0 --port 8081 --no-auth

# Run as REST API (port 8081)
docker run -p 8081:8081 sympy-mcp uv run sympy-mcp --mode rest --host 0.0.0.0 --port 8081 --no-auth
```

Or use Docker Compose from the `docker/` directory, which starts both services simultaneously:

```bash
cd docker
docker compose up -d --build
```

This starts:
- `sympy-mcp-rest` — REST API on **port 8081**
- `sympy-mcp-mcp` — MCP HTTP server on **port 8082** (`/mcp` endpoint)

Alternatively, pull the pre-built image from GitHub Container Registry:

```bash
docker pull ghcr.io/sdiehl/sympy-mcp:main
docker run -p 8081:8081 --rm ghcr.io/sdiehl/sympy-mcp:main \
  uv run sympy-mcp --mode mcp --host 0.0.0.0 --port 8081 --no-auth
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

**Assistant**: (Internal tool call) `intro_many` to introduce variables:
```json
{
  "variables": [
    {"var_name": "t", "pos_assumptions": ["real"], "neg_assumptions": []},
    {"var_name": "m", "pos_assumptions": ["real", "positive"], "neg_assumptions": []},
    {"var_name": "c", "pos_assumptions": ["real", "positive"], "neg_assumptions": []},
    {"var_name": "k", "pos_assumptions": ["real", "positive"], "neg_assumptions": []}
  ]
}
```

**Assistant**: (Internal tool call) `introduce_function` to define x(t):
```json
{
  "func_name": "x"
}
```

**Assistant**: (Internal tool call) `introduce_expression` to create the differential equation:
```json
{
  "expr_str": "Eq(m*Derivative(x(t), t, t) + c*Derivative(x(t), t) + k*x(t), F(t))"
}
```

**Assistant**: (Internal tool call) `print_latex_expression` to display the equation nicely:
```json
{
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
  "func_name": "F"
}
```

**Assistant**: (Internal tool call) `dsolve_ode` to solve the differential equation:
```json
{
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

**Assistant**: (Internal tool call) `create_predefined_metric` to create the Anti-de Sitter metric:
```json
{
  "metric_name": "AntiDeSitter"
}
```

**Assistant**: (Internal tool call) `calculate_tensor` to calculate the Ricci tensor:
```json
{
  "metric_key": "metric_AntiDeSitter",
  "tensor_type": "RICCI_TENSOR",
  "simplify_result": true
}
```

**Assistant**: (Internal tool call) `print_latex_tensor` to display the Ricci tensor:
```json
{
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
  "metric_key": "metric_AntiDeSitter",
  "tensor_type": "RICCI_SCALAR",
  "simplify_result": true
}
```

**Assistant**: (Internal tool call) `print_latex_tensor` to display the Ricci scalar:
```json
{
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
5. `dsolve_ode` × 2 — solve the coupled system; apply initial conditions via `substitute_expression`
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
