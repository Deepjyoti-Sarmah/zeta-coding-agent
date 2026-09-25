import { useState } from "react";

const OPTIONS = [
  { id: "uv", label: "uv", cmd: "uv tool install zeta-ai" },
  { id: "pipx", label: "pipx", cmd: "pipx install zeta-ai" },
  { id: "pip", label: "pip", cmd: "pip install zeta-ai" },
] as const;

export function InstallTabs() {
  const [active, setActive] = useState<(typeof OPTIONS)[number]["id"]>("uv");
  const [copied, setCopied] = useState(false);
  const option = OPTIONS.find((o) => o.id === active) ?? OPTIONS[0];

  async function copy() {
    try {
      await navigator.clipboard.writeText(option.cmd);
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch {
      // clipboard unavailable — ignore
    }
  }

  return (
    <div className="install-wrap">
      <span className="install-label">Install</span>
      <div className="install-block">
        <div className="install-tabs" role="tablist" aria-label="Package manager">
          {OPTIONS.map((o) => (
            <button
              key={o.id}
              role="tab"
              aria-selected={o.id === active}
              onClick={() => setActive(o.id)}
              type="button"
            >
              {o.label}
            </button>
          ))}
        </div>
        <div className="install-row">
          <span className="install-cmd">
            <span className="dollar">$</span> {option.cmd}
          </span>
          <button
            className="copy"
            type="button"
            aria-label="Copy install command"
            onClick={copy}
          >
            {copied ? "copied ✓" : "copy"}
          </button>
        </div>
      </div>
    </div>
  );
}
