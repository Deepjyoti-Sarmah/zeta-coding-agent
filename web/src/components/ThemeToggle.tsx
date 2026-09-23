import { useEffect, useState } from "react";

type Theme = "auto" | "light" | "dark";

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  if (theme === "auto") {
    root.removeAttribute("data-theme");
  } else {
    root.setAttribute("data-theme", theme);
  }
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(() => {
    try {
      return (localStorage.getItem("zeta-theme") as Theme) || "auto";
    } catch {
      return "auto";
    }
  });

  useEffect(() => {
    applyTheme(theme);
    try {
      localStorage.setItem("zeta-theme", theme);
    } catch {
      // storage unavailable — theme still applies for this load
    }
  }, [theme]);

  return (
    <div className="theme-toggle" role="group" aria-label="Theme">
      {(["auto", "light", "dark"] as const).map((t) => (
        <button
          key={t}
          type="button"
          aria-pressed={theme === t}
          onClick={() => setTheme(t)}
        >
          {t}
        </button>
      ))}
    </div>
  );
}
