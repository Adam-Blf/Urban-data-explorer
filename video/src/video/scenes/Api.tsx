import { AbsoluteFill } from "remotion";
import { COLORS, FONT, MONO } from "../theme";
import { useSlideUp } from "../helpers";

const ENDPOINTS = [
    { v: "POST", p: "/auth/login",                          d: "username/password → JWT", c: COLORS.accent3 },
    { v: "GET",  p: "/health",                              d: "liveness + version",       c: COLORS.fg1 },
    { v: "GET",  p: "/datamarts/arrondissements",           d: "KPI · pagination · filtres", c: COLORS.accent2 },
    { v: "GET",  p: "/datamarts/timeline",                  d: "série mensuelle prix m²",  c: COLORS.accent2 },
    { v: "GET",  p: "/datamarts/indicators",                d: "4 indicateurs pivotés",    c: COLORS.accent2 },
    { v: "GET",  p: "/geo/arrondissements.geojson",         d: "fond enrichi des KPI",     c: COLORS.accent },
    { v: "GET",  p: "/geo/poi.geojson",                     d: "POI filtrables par catégorie", c: COLORS.accent },
];

export const Api: React.FC = () => (
    <AbsoluteFill style={{ fontFamily: FONT, color: COLORS.fg0, padding: 120 }}>
        <div style={{ fontSize: 16, color: COLORS.accent, letterSpacing: "0.18em",
                      fontWeight: 700, marginBottom: 16 }}>
            05 · API REST FastAPI
        </div>
        <h2 style={{ fontSize: 64, fontWeight: 800, margin: 0,
                     letterSpacing: "-0.03em", marginBottom: 56, ...useSlideUp(0) }}>
            JWT · pagination · filtres · OpenAPI auto.
        </h2>
        {ENDPOINTS.map((e, i) => (
            <div key={i} style={{
                display: "flex", alignItems: "center", gap: 24, marginBottom: 14,
                ...useSlideUp(15 + i * 6),
            }}>
                <div style={{
                    width: 96, padding: "10px 0", textAlign: "center",
                    background: e.c, color: COLORS.bg0, borderRadius: 12,
                    fontWeight: 800, fontSize: 18,
                }}>
                    {e.v}
                </div>
                <div style={{ fontFamily: MONO, fontSize: 26, fontWeight: 700, flex: "0 0 620px" }}>
                    {e.p}
                </div>
                <div style={{ color: COLORS.fg1, fontSize: 20 }}>{e.d}</div>
            </div>
        ))}
    </AbsoluteFill>
);
