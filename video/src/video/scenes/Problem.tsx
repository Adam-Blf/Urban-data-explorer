import { AbsoluteFill } from "remotion";
import { COLORS, FONT } from "../theme";
import { useSlideUp } from "../helpers";

const KPIs = [
    { big: "> 10 000 €", lbl: "prix m² médian intra-muros", color: COLORS.accent },
    { big: "17 sources", lbl: "données ouvertes hétérogènes", color: COLORS.accent2 },
    { big: "20 arr.",    lbl: "réalités économiques différentes", color: COLORS.accent3 },
];

export const Problem: React.FC = () => {
    const t = useSlideUp(10);
    return (
        <AbsoluteFill style={{ fontFamily: FONT, color: COLORS.fg0, padding: 120 }}>
            <div style={{ fontSize: 16, color: COLORS.accent3, letterSpacing: "0.18em",
                          fontWeight: 700, marginBottom: 24, ...useSlideUp(0) }}>
                01 · LE PROBLÈME
            </div>
            <h2 style={{ fontSize: 88, fontWeight: 800, margin: 0,
                         letterSpacing: "-0.03em", lineHeight: 1.05, ...t }}>
                Paris,<br />marché du logement<br />fragmenté, illisible.
            </h2>
            <div style={{ display: "flex", gap: 32, marginTop: 80, ...useSlideUp(35) }}>
                {KPIs.map((k, i) => (
                    <div key={i} style={{
                        flex: 1, background: COLORS.bg2, borderRadius: 24, padding: 40,
                    }}>
                        <div style={{ fontSize: 56, fontWeight: 800, color: k.color }}>
                            {k.big}
                        </div>
                        <div style={{ marginTop: 12, color: COLORS.fg1, fontSize: 20 }}>
                            {k.lbl}
                        </div>
                    </div>
                ))}
            </div>
            <p style={{ fontSize: 26, marginTop: 80, color: COLORS.fg0,
                        lineHeight: 1.4, ...useSlideUp(60) }}>
                Comment lire ce marché à l'échelle de l'arrondissement,
                en un seul écran, croisé avec revenus, équipements, environnement&nbsp;?
            </p>
        </AbsoluteFill>
    );
};
