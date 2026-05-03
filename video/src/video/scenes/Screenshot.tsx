import { AbsoluteFill, Img, staticFile } from "remotion";
import { COLORS, FONT } from "../theme";
import { useFadeIn, useSlideUp } from "../helpers";

interface Props {
    src: string;
    title: string;
}

export const Screenshot: React.FC<Props> = ({ src, title }) => {
    const fade = useFadeIn(20);
    const slide = useSlideUp(0);
    return (
        <AbsoluteFill style={{ fontFamily: FONT, color: COLORS.fg0, padding: 80 }}>
            <h2 style={{
                fontSize: 44, fontWeight: 800, margin: 0,
                letterSpacing: "-0.03em", marginBottom: 24,
                ...slide,
            }}>
                {title}
            </h2>
            <div style={{
                flex: 1, display: "flex", justifyContent: "center", alignItems: "center",
                opacity: fade,
            }}>
                <Img
                    src={staticFile(`screenshots/${src}`)}
                    style={{
                        maxWidth: "100%", maxHeight: "100%",
                        borderRadius: 18,
                        border: `1px solid ${COLORS.bg2}`,
                        boxShadow: "0 30px 80px -30px rgba(0,0,0,0.7)",
                    }}
                />
            </div>
        </AbsoluteFill>
    );
};
