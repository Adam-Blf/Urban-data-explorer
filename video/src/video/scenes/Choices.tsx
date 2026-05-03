import { AbsoluteFill } from "remotion";
import { COLORS, FONT } from "../theme";
import { useSlideUp } from "../helpers";

const ITEMS = [
    { tag: "ADR-001", title: "Polars + DuckDB > Spark",        sub: "Volume cible RAM-friendly · 5× plus léger · démarrage instant",  color: COLORS.accent },
    { tag: "ADR-002", title: "Partitionnement year/month/day", sub: "Idempotence stricte · replays sans doublons",                    color: COLORS.accent2 },
    { tag: "ADR-003", title: "Indicateurs en z-score",         sub: "Lecture comparable, robuste à l'évolution mensuelle",            color: COLORS.accent3 },
    { tag: "ADR-004", title: "DuckDB read-only par requête",   sub: "Pas de pool · lecture concurrente sécurisée",                    color: COLORS.blue },
    { tag: "ADR-005", title: "Frontend statique CDN-only",     sub: "Démo en 5 min sur n'importe quel host · zéro bundler",          color: COLORS.fg0 },
];

export const Choices: React.FC = () => (
    <AbsoluteFill style={{ fontFamily: FONT, color: COLORS.fg0, padding: 120 }}>
        <div style={{ fontSize: 16, color: COLORS.accent, letterSpacing: "0.18em",
                      fontWeight: 700, marginBottom: 16 }}>
            06 · CHOIX TECHNIQUES
        </div>
        <h2 style={{ fontSize: 56, fontWeight: 800, margin: 0,
                     letterSpacing: "-0.03em", marginBottom: 56, ...useSlideUp(0) }}>
            5 ADRs documentés.
        </h2>
        {ITEMS.map((it, i) => (
            <div key={i} style={{
                display: "flex", alignItems: "center", gap: 32, marginBottom: 18,
                ...useSlideUp(15 + i * 8),
            }}>
                <div style={{
                    width: 200, padding: "14px 22px", textAlign: "center",
                    background: it.color, color: COLORS.bg0,
                    borderRadius: 14, fontWeight: 800, fontSize: 18,
                }}>
                    {it.tag}
                </div>
                <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 26, fontWeight: 700 }}>{it.title}</div>
                    <div style={{ fontSize: 18, color: COLORS.fg1, marginTop: 4 }}>{it.sub}</div>
                </div>
            </div>
        ))}
    </AbsoluteFill>
);
