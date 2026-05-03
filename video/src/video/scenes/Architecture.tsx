import { AbsoluteFill } from "remotion";
import { COLORS, FONT } from "../theme";
import { useSlideUp } from "../helpers";

const LAYERS = [
    { tag: "BRONZE",   color: COLORS.accent,  title: "Snapshot brut versionné Parquet", sub: "feeder.py · partitionnement year=YYYY/month=MM/day=DD" },
    { tag: "SILVER",   color: COLORS.accent2, title: "Cleaning · 6 règles · joints · windows", sub: "processor.py · Polars + Shapely + cache" },
    { tag: "GOLD",     color: COLORS.accent3, title: "DuckDB · dim, facts, KPI, timeline", sub: "datamart.py · 4 indicateurs composites" },
    { tag: "API",      color: COLORS.blue,    title: "FastAPI · JWT · pagination · filtres", sub: "uvicorn :8000 · OpenAPI auto" },
    { tag: "FRONTEND", color: COLORS.fg0,     title: "MapLibre + Chart.js · 4 niveaux carto", sub: "ESM via CDN · zéro build · Vercel ready" },
];

export const Architecture: React.FC = () => (
    <AbsoluteFill style={{ fontFamily: FONT, color: COLORS.fg0, padding: 120 }}>
        <div style={{ fontSize: 16, color: COLORS.accent, letterSpacing: "0.18em",
                      fontWeight: 700, marginBottom: 24 }}>
            03 · ARCHITECTURE
        </div>
        <h2 style={{ fontSize: 56, fontWeight: 800, margin: 0,
                     letterSpacing: "-0.03em", marginBottom: 56, ...useSlideUp(0) }}>
            Pipeline médaillon · Bronze → Silver → Gold
        </h2>

        {LAYERS.map((l, i) => (
            <div key={i} style={{
                display: "flex", alignItems: "center", gap: 32,
                marginBottom: 18,
                ...useSlideUp(15 + i * 10),
            }}>
                <div style={{
                    width: 220, padding: "16px 24px",
                    background: l.color, color: COLORS.bg0,
                    borderRadius: 16, fontWeight: 800, fontSize: 22,
                    textAlign: "center",
                }}>
                    {l.tag}
                </div>
                <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 24, fontWeight: 700 }}>{l.title}</div>
                    <div style={{ fontSize: 16, color: COLORS.fg1, marginTop: 4 }}>{l.sub}</div>
                </div>
            </div>
        ))}
    </AbsoluteFill>
);
