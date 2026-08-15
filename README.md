# 🌌 Neuro-Symbolic Hypothesis & Symbolic Regression Engine
> **An autonomous quantitative discovery agent that extracts governing mathematical laws from raw empirical datasets.**
> *Developed for the Reverie Hacks DevOps & AI Hackathon 2026*

---

## 🚀 Core Architecture

The engine combines high-level creative reasoning from **Large Language Models (Featherless AI)** with fast, deterministic numerical methods (**SciPy/SymPy**) and programmatic local structural evolution (**Expression Tree mutation**).

```
   ┌────────────────────────────────────────────────────────┐
   │                  1. DOMAIN SCRAPING                    │
   │   User uploads CSV + enters context (e.g. Astro)       │
   │   └─► Firecrawl searches arXiv/Scholar for formulas    │
   └──────────────────────────┬─────────────────────────────┘
                              │ Scraped paper markdown
                              ▼
   ┌────────────────────────────────────────────────────────┐
   │                2. CANDIDATE GENERATION                 │
   │   LLM (Featherless AI) generates 5 seed equations      │
   │   incorporating scraped structures (e.g. Keplerian)    │
   └──────────────────────────┬─────────────────────────────┘
                              │ Raw equation string
                              ▼
   ┌────────────────────────────────────────────────────────┐
   │                 3. AST SAFETY SANDBOX                  │
   │   Checks formula syntax against whitelist.             │
   │   Blocks python builtins. Allows custom case params.   │
   └──────────────────────────┬─────────────────────────────┘
                              │ Safe SymPy expression
                              ▼
   ┌────────────────────────────────────────────────────────┐
   │                4. PARAMETER OPTIMIZATION               │
   │   SciPy curve_fit solves exact parameter floats.       │
   │   Calculates R^2, AIC, and BIC metrics.               │
   └──────────────────────────┬─────────────────────────────┘
                              │ Successful fit (Seed)
                              ▼
   ┌────────────────────────────────────────────────────────┐
   │              5. LOCAL TREE MUTATIONS                   │
   │   Converts equation to mathematical node tree.         │
   │   Mutates operators, expands subtrees, folds constants │
   │   WITHOUT calling LLM again. Retries step 3 & 4.       │
   └──────────────────────────┬─────────────────────────────┘
                              │ Best models
                              ▼
   ┌────────────────────────────────────────────────────────┐
   │                  6. DYNAMIC DASHBOARD                  │
   │   Leaderboard sorted by R^2 & AIC.                     │
   │   Interactive Chart.js plots raw scatter vs fit line.  │
   └────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack & Integrations

* **Inference Pipeline**: **Featherless AI** (utilizing `Qwen2.5-Coder-32B-Instruct` for mathematical logic).
* **Research Search**: **Firecrawl V2 Search API** (crawls/scrapes scientific documentation to retrieve formulas).
* **Math Solver & Sandbox**: **SymPy** (symbolic simplification, safety verification) & **SciPy** (non-linear least squares optimization).
* **Deployment Blueprint**: **Render** (Auto-deploys via `render.yaml` with Python 3.11.6 runtime).
* **Interactive Frontend**: Vanilla CSS glassmorphic dashboard with **Chart.js** dynamic regression plotting.

---

## 📊 Live Verification Results

The engine has been rigorously tested locally across multiple physical and scientific domains:

### 1. Galactic Rotation Velocity Curves (Dark Matter/MOND)
* **Observed Data**: Flat asymptotic orbital velocities of outer stars.
* **Engine Discovered Equation**: $v(r) = a \cdot \ln(b \cdot r + c)$
* **Parameters**: $a \approx 32.50$, $b \approx 23.81$, $c \approx -8.66$
* **Performance**: $R^2 = 0.9777$ (Typical error $< 1\%$).

### 2. Damped Harmonic Oscillator (Acoustics & Waves)
* **Observed Data**: Sinusoidal waves decaying exponentially with noise.
* **Engine Discovered Equation**: $v(t) = A \cdot e^{-\lambda \cdot t} \cdot \sin(\omega \cdot t + \phi)$
* **Performance**: $R^2 = 0.9966$ (AIC: $-477.23$).

### 3. Piecewise Step Functions (Digital Signals)
* **Observed Data**: Hard discontinuous state jump from $-1.0$ to $+1.0$.
* **Engine Discovered Equation**: $y(x) = \tanh(a \cdot x)$ (where $a \to \infty$)
* **Performance**: $R^2 = 1.0000$ (discovers a smooth, differentiable approximation of step functions).

---

## 🔒 Safety & Resilience Features

1. **AST Whitelist Execution**: The code sandbox strictly whitelists math operations (`Add`, `Sub`, `Mul`, `Div`, `Pow`, `sin`, `cos`, etc.) and blocks Python built-ins like `__import__` or `eval` to prevent code injection.
2. **Infinite Float / NaN Sanitization**: Automatically intercepts optimization overflows (`NaN`, `Infinity`, `-Infinity`) and serializes them to valid JSON `null` values, preventing browser parsing crashes.
3. **Cache-Busting Integration**: Scripts are bundled with automatic cache-busting query strings (`?v=1.0.2`) to force modern browsers (Chrome/Safari) to run the latest UI patches.

---

## 🚀 Quick Start (Local Run)

### 1. Clone & Install Dependencies
Ensure you have `python 3.11` installed:
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Configure your environment variables or update `config.py`:
```bash
export FEATHERLESS_API_KEY="your-featherless-key"
export FIRECRAWL_API_KEY="fc-edd3db0c3f3849d099eca9ddc77248e8"
```

### 3. Run the Server
```bash
uvicorn main:app --reload
```
Open `http://127.0.0.1:8000` in your web browser, upload any CSV dataset, and witness autonomous math discovery in action!

---

## ☁️ Production Cloud Deployment

To deploy this project to Render:
1. Push this folder to your private GitHub repository.
2. Go to `dashboard.render.com` -> **Blueprints** -> **New Blueprint Instance**.
3. Connect your repository. Render will read `render.yaml` and set up the domain, environment, and dependencies automatically.
