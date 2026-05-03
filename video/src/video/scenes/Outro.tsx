import { AbsoluteFill, Img, staticFile } from "remotion";
import { COLORS, FONT, MONO } from "../theme";
import { useFadeIn, useSlideUp } from "../helpers";

export const Outro: React.FC = () => {
    const fade = useFadeIn(20);
    const slide = useSlideUp(15);
    return (
        <AbsoluteFill style={{
            background: `linear-gradient(180deg, ${COLORS.bg1}, ${COLORS.bg0})`,
            fontFamily: FONT, color: COLORS.fg0,
            justifyContent: "center", alignItems: "center", padding: 80,
        }}>
            <Img
                src={staticFile("efrei-logo-white.png")}
                style={{ height: 88, opacity: fade, marginBottom: 50 }}
            />
            <h2 style={{
                fontSize: 140, fontWeight: 800, margin: 0,
                letterSpacing: "-0.03em", ...slide,
            }}>
                Merci.
            </h2>
            <p style={{
                fontFamily: MONO, fontSize: 28, color: COLORS.accent2,
                marginTop: 40, ...slide,
            }}>
                github.com/Adam-Blf/urban-data-explorer
            </p>
            <div style={{ marginTop: 60, display: "flex", gap: 48, fontSize: 24 }}>
                <span style={{ color: COLORS.accent, fontWeight: 700 }}>Adam Beloucif</span>
                <span style={{ color: COLORS.fg1 }}>+</span>
                <span style={{ color: COLORS.accent2, fontWeight: 700 }}>Emilien Morice</span>
            </div>
        </AbsoluteFill>
    );
};
