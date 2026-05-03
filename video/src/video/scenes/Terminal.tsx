import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { COLORS, FONT, MONO } from "../theme";
import { useSlideUp } from "../helpers";

const LINES = [
    { txt: "$ python -m pipeline.feeder --source dvf --year 2024",                     color: COLORS.accent },
    { txt: "feeder · DVF · downloading https://files.data.gouv.fr/geo-dvf/.../full.csv.gz", color: COLORS.fg1 },
    { txt: "feeder · DVF · filtered 4 213 552 → 252 481 rows (Paris only)",            color: COLORS.fg1 },
    { txt: "feeder · OK (source=dvf)",                                                  color: COLORS.accent2 },
    { txt: "",                                                                          color: COLORS.fg1 },
    { txt: "$ python -m pipeline.processor --source dvf",                              color: COLORS.accent },
    { txt: "validation · rule=non_null_date         rejected=0      kept=252 481",     color: COLORS.fg1 },
    { txt: "validation · rule=valeur_realistic      rejected=8 124  kept=244 357",     color: COLORS.fg1 },
    { txt: "validation · rule=geo_within_paris      rejected=312    kept=244 045",     color: COLORS.fg1 },
    { txt: "dvf · cached silver dataframe in memory",                                  color: COLORS.fg1 },
    { txt: "processor · OK · wrote silver/dvf/year=2024/month=05/day=03/dvf.parquet",  color: COLORS.accent2 },
    { txt: "",                                                                          color: COLORS.fg1 },
    { txt: "$ python -m pipeline.datamart --build all",                                color: COLORS.accent },
    { txt: "gold · building dim_arrondissement · fact_transactions_arr_mois ·",        color: COLORS.fg1 },
    { txt: "       fact_logements_sociaux · fact_revenus_arr · fact_air_quality ·",    color: COLORS.fg1 },
    { txt: "       fact_poi_arr · kpi_arrondissement (4 composite indicators) ·",      color: COLORS.fg1 },
    { txt: "       timeline_arrondissement",                                           color: COLORS.fg1 },
    { txt: "datamart · OK · DB at data/gold/urban.duckdb",                             color: COLORS.accent2 },
];

export const Terminal: React.FC = () => {
    const frame = useCurrentFrame();
    const headerStyle = useSlideUp(0);
    return (
        <AbsoluteFill style={{ fontFamily: FONT, color: COLORS.fg0, padding: 100 }}>
            <div style={{ fontSize: 16, color: COLORS.accent, letterSpacing: "0.18em",
                          fontWeight: 700, marginBottom: 16, ...headerStyle }}>
                04 · PIPELINE EN ACTION
            </div>
            <h2 style={{ fontSize: 48, fontWeight: 800, margin: 0,
                         letterSpacing: "-0.03em", marginBottom: 32, ...headerStyle }}>
                Idempotent · paramétrable · loggué.
            </h2>
            <div style={{
                fontFamily: MONO, fontSize: 22, lineHeight: 1.55,
                background: "#06091a", border: `1px solid ${COLORS.bg2}`,
                borderRadius: 18, padding: 40, height: 720, overflow: "hidden",
            }}>
                {LINES.map((l, i) => {
                    const reveal = Math.max(0, frame - 30 - i * 4);
                    const opacity = interpolate(reveal, [0, 6], [0, 1], { extrapolateRight: "clamp" });
                    const cw = interpolate(reveal, [0, 12], [0, 1], { extrapolateRight: "clamp" });
                    return (
                        <div key={i} style={{
                            color: l.color, opacity,
                            whiteSpace: "nowrap", overflow: "hidden",
                            width: `${cw * 100}%`,
                        }}>
                            {l.txt || " "}
                        </div>
                    );
                })}
            </div>
        </AbsoluteFill>
    );
};
