import "./App.css";
import { InstallTabs } from "./components/InstallTabs";
import { ThemeToggle } from "./components/ThemeToggle";

const GITHUB = "https://github.com/Deepjyoti-Sarmah/zeta-coding-agent";
const DOCS = `${GITHUB}#readme`;
const ROADMAP = `${GITHUB}/issues`;

function App() {
  return (
    <>
      <div className="bg-fade" aria-hidden="true" />
      <div className="margin-line" aria-hidden="true" />

      <div className="wrap">
        <nav>
          <div className="brand">
            <span className="glyph">&#950;</span>
            <span className="name">zeta</span>
            <span className="ver">v0.3</span>
          </div>
          <div className="navlinks">
            <a href={DOCS}>Docs</a>
            <a href={ROADMAP}>Roadmap</a>
            <a href="#start">Getting started</a>
            <a className="gh" href={GITHUB}>
              GitHub &#8599;
            </a>
            <ThemeToggle />
          </div>
        </nav>

        <header>
          <div className="hero-center">
            <p className="eyebrow">A minimalist coding-agent harness</p>
            <h1>
              A coding agent
              <br />
              small enough to <em>read.</em>
            </h1>
            <p className="lede">
              <strong>Zeta</strong> is a terminal coding agent in Python — and a
              phase-by-phase reference for how one is actually built. Named for{" "}
              <span className="zeta-glyph">&#950;</span>, the function built by
              adding one term at a time, nothing hidden.
            </p>
            <div className="cta-row">
              <InstallTabs />
              <a className="ghost" href={DOCS}>
                Read the docs <span className="arr">&rarr;</span>
              </a>
            </div>
          </div>

          <div className="strip">
            <div className="cellitem">
              <span className="num">3</span>
              <span className="cap">small layers</span>
            </div>
            <div className="cellitem">
              <span className="num">0</span>
              <span className="cap">magic</span>
            </div>
          </div>
        </header>
      </div>

      <div className="wrap">
        <section id="start">
          <div className="sec-head">
            <span className="mark">01</span>
            <h2>Three layers, each explainable on its own</h2>
          </div>
          <div className="layers">
            <div className="layer">
              <span className="idx">&#8544;</span>
              <span className="pkg">zeta_ai</span>
              <h3>The provider</h3>
              <p>
                Models stream events. A thin layer turns provider responses into a
                single, ordered event stream you can follow line by line.
              </p>
            </div>
            <div className="layer">
              <span className="idx">&#8545;</span>
              <span className="pkg">zeta_agent</span>
              <h3>The harness</h3>
              <p>
                A portable brain: the loop that turns events into tool calls, owns
                transcript and session state, and stays free of any one app.
              </p>
            </div>
            <div className="layer">
              <span className="idx">&#8546;</span>
              <span className="pkg">zeta_coding</span>
              <h3>The agent</h3>
              <p>
                Files, shell, sessions, skills, commands, and a terminal UI — one
                concrete coding environment built on the harness.
              </p>
            </div>
          </div>
        </section>

        <section>
          <div className="two">
            <div>
              <p className="eyebrow">The boundary</p>
              <h2>A reusable brain, a swappable body.</h2>
              <p>
                The <span className="zeta-glyph">&#950;</span> harness is the
                agent. The session is its environment. The terminal is just one
                possible face. Keep them apart and the whole thing stays legible.
              </p>
            </div>
            <div className="terminal" aria-hidden="true">
              <div className="bar">
                <span></span>
                <span></span>
                <span></span>
                <span className="t">zeta — session</span>
              </div>
              <pre>
                <span className="pmt">&#950; &rsaquo;</span>{" "}
                <span className="cmd">fix the failing test in parser.py</span>
                {"\n\n"}
                <span className="out">  reading  </span>
                <span className="key">parser.py</span>
                <span className="out">, </span>
                <span className="key">test_parser.py</span>
                {"\n"}
                <span className="out">  edit     </span>
                <span className="key">parser.py</span>
                <span className="out">  +4 &minus;1</span>
                {"\n"}
                <span className="out">  run      </span>
                <span className="key">uv run pytest -q</span>
                {"\n"}
                <span className="out">  &check; 1 passed in 0.21s</span>
                {"\n\n"}
                <span className="pmt">&#950; &rsaquo;</span>{" "}
                <span className="cmd">_</span>
              </pre>
            </div>
          </div>
        </section>

        <section>
          <div className="sec-head">
            <span className="mark">02</span>
            <h2>15+ providers, one event stream</h2>
          </div>
          <p className="lede" style={{ maxWidth: "42em" }}>
            Switch models without switching mental models. Every provider is
            normalized to the same stream of events before it ever reaches the
            harness.
          </p>
          <div className="chip-row">
            {[
              "Anthropic",
              "OpenAI",
              "OpenAI Codex",
              "Google",
              "Mistral",
              "OpenAI-compatible",
              "Fake (tests)",
            ].map((p) => (
              <span className="chip" key={p}>
                {p}
              </span>
            ))}
          </div>
        </section>

        <section>
          <div className="sec-head">
            <span className="mark">03</span>
            <h2>The philosophy</h2>
          </div>
          <div className="principles">
            <div className="pr">
              <h3>Small layers beat magic</h3>
              <p>
                Every package has one job and can be explained without the
                others. No framework you have to believe in.
              </p>
            </div>
            <div className="pr">
              <h3>Explicit over clever</h3>
              <p>
                The control flow is on the page. Streaming, tool calls, sessions —
                readable top to bottom.
              </p>
            </div>
            <div className="pr">
              <h3>Built phase by phase</h3>
              <p>
                Each commit adds one understandable piece, so the repo doubles as
                a course in how agents are assembled.
              </p>
            </div>
            <div className="pr">
              <h3>Usable, not just instructive</h3>
              <p>
                It is a real terminal agent you can run today — the teaching is a
                side effect of the design, not a toy.
              </p>
            </div>
          </div>
        </section>

        <section className="closing">
          <span className="turn">&#950;</span>
          <p>
            Start the loop. Watch a coding agent run with nothing hidden between
            you and the code.
          </p>
          <div className="cta-row">
            <InstallTabs />
            <a className="ghost" href={GITHUB}>
              View on GitHub <span className="arr">&rarr;</span>
            </a>
          </div>
        </section>

        <footer>
          <div className="brand">
            <span className="glyph" style={{ fontSize: "20px" }}>
              &#950;
            </span>
            <span className="name">zeta</span>
          </div>
          <div className="l">
            <a href={DOCS}>Docs</a>
            <a href={GITHUB}>GitHub</a>
            <a href={ROADMAP}>Roadmap</a>
          </div>
          <span>A teaching project &middot; inspired by Pi</span>
        </footer>
      </div>
    </>
  );
}

export default App;
