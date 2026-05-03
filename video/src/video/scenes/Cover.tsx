import { AbsoluteFill, Img, staticFile } from "remotion";
import { COLORS, FONT } from "../theme";
import { useFadeIn, useSlideUp } from "../helpers";

export const Cover: React.FC = () => {
    const fade = useFadeIn(20);
    const a = useSlideUp(15);
    const b = useSlideUp(35);
    const c = useSlideUp(55);

    return (
        <AbsoluteFill style={{
            background: `linear-gradient(180deg, ${COLORS.bg1} 0%, ${COLORS.bg0} 100%)`,
            fontFamily: FONT,
            color: COLORS.fg0,
            justifyContent: "center",
            alignItems: "center",
            padding: 80,
        }}>
            <Img
                src={staticFile("efrei-logo-white.png")}
                style={{ height: 110, opacity: fade, marginBottom: 60 }}
            />
            <h1 style={{
                fontSize: 110, fontWeight: 800, margin: 0,
                letterSpacing: "-0.03em", textAlign: "center",
                ...a,
            }}>
                Urban Data Explorer
            </h1>
            <p style={{
                fontSize: 28, color: COLORS.fg1, marginTop: 24, textAlign: "center",
                maxWidth: 1200, lineHeight: 1.4, ...b,
            }}>
                Plateforme open data Paris · pipeline médaillon, API REST sécurisée
                et dashboard cartographique du logement parisien.
            </p>
            <div style={{
                marginTop: 70, display: "flex", gap: 32,
                fontSize: 22, ...c,
            }}>
                <span style={{ color: COLORS.accent, fontWeight: 700 }}>Adam Beloucif</span>
                <span style={{ color: COLORS.fg1 }}>+</span>
                <span style={{ color: COLORS.accent2, fontWeight: 700 }}>Emilien Morice</span>
            </div>
            <p style={{ fontSize: 18, color: COLORS.fg1, marginTop: 30, ...c }}>
                M1 Data Engineering &amp; IA · EFREI Paris · Architecture de Données · 2026
            </p>
        </AbsoluteFill>
    );
};
