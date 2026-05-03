import { AbsoluteFill } from "remotion";
import { COLORS, FONT } from "../theme";
import { useSlideUp } from "../helpers";

const CARDS = [
    { big: "17", mid: "sources",                sub: "data.gouv · OpenData Paris · INSEE · Airparif", color: COLORS.accent },
    { big: "4",  mid: "indicateurs composites", sub: "accessibilité · tension · effort social · attractivité", color: COLORS.accent2 },
    { big: "4",  mid: "niveaux carto",          sub: "choroplèthe · POI · timeline · comparaison", color: COLORS.accent3 },
    { big: "29", mid: "commits granulaires",    sub: "alternance Adam ↔ Emilien", color: COLORS.blue },
];

export const Answer: React.FC = () => (
    <AbsoluteFill style={{ fontFamily: FONT, color: COLORS.fg0, padding: 120 }}>
        <div style={{ fontSize: 16, color: COLORS.accent, letterSpacing: "0.18em",
                      fontWeight: 700, marginBottom: 24, ...useSlideUp(0) }}>
            02 · LA RÉPONSE
        </div>
        <h2 style={{ fontSize: 96, fontWeight: 800, margin: 0,
                     letterSpacing: "-0.03em", ...useSlideUp(10) }}>
            Médaillon · API · Dashboard.
        </h2>
        <p style={{ fontSize: 26, color: COLORS.fg1, marginTop: 24, ...useSlideUp(25) }}>
            Une plateforme complète, du pipeline d'ingestion à la carto interactive.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)",
                      gap: 24, marginTop: 80, ...useSlideUp(40) }}>
            {CARDS.map((c, i) => (
                <div key={i} style={{ background: COLORS.bg2, borderRadius: 24, padding: 32 }}>
                    <div style={{ fontSize: 84, fontWeight: 800, color: c.color, lineHeight: 1 }}>
                        {c.big}
                    </div>
                    <div style={{ marginTop: 12, fontSize: 18, fontWeight: 700 }}>
                        {c.mid}
                    </div>
                    <div style={{ marginTop: 8, color: COLORS.fg1, fontSize: 14, lineHeight: 1.5 }}>
                        {c.sub}
                    </div>
                </div>
            ))}
        </div>
    </AbsoluteFill>
);
