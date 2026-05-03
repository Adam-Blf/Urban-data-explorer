/**
 * Urban Data Explorer · vidéo de démo soutenance
 * Format · 1920×1080, 30 fps. Durée cible · 5 min 40 (10 200 frames).
 *
 * 12 scènes scriptées suivant docs/DEMO_SCRIPT.md ·
 *   1. Cover (logo EFREI + titre)              [00:00 - 00:25]
 *   2. Le problème                              [00:25 - 00:55]
 *   3. La réponse · 17 sources, 4 indicateurs   [00:55 - 01:25]
 *   4. Architecture médaillon                   [01:25 - 02:00]
 *   5. Pipeline en action (terminal)            [02:00 - 02:40]
 *   6. API REST FastAPI                         [02:40 - 03:10]
 *   7. Dashboard · choroplèthe prix             [03:10 - 03:40]
 *   8. Choroplèthe attractivité                 [03:40 - 04:05]
 *   9. Couches POI activables                   [04:05 - 04:35]
 *  10. Mode comparaison                         [04:35 - 05:05]
 *  11. Choix techniques + qualité               [05:05 - 05:30]
 *  12. Outro · repo + équipe                    [05:30 - 05:40]
 */

import { AbsoluteFill, Sequence } from "remotion";
import { Cover } from "./scenes/Cover";
import { Problem } from "./scenes/Problem";
import { Answer } from "./scenes/Answer";
import { Architecture } from "./scenes/Architecture";
import { Terminal } from "./scenes/Terminal";
import { Api } from "./scenes/Api";
import { Screenshot } from "./scenes/Screenshot";
import { Choices } from "./scenes/Choices";
import { Outro } from "./scenes/Outro";

export const FPS = 30;
const s = (sec: number) => Math.round(sec * FPS);

const SCENES = [
    { from: s(0),     dur: s(25), comp: <Cover /> },
    { from: s(25),    dur: s(30), comp: <Problem /> },
    { from: s(55),    dur: s(30), comp: <Answer /> },
    { from: s(85),    dur: s(35), comp: <Architecture /> },
    { from: s(120),   dur: s(40), comp: <Terminal /> },
    { from: s(160),   dur: s(30), comp: <Api /> },
    { from: s(190),   dur: s(30), comp: <Screenshot src="02-choropleth-prix.png"
                                             title="Choroplèthe · prix m² médian" /> },
    { from: s(220),   dur: s(25), comp: <Screenshot src="03-choropleth-attractivite.png"
                                             title="Indice composite d'attractivité" /> },
    { from: s(245),   dur: s(30), comp: <Screenshot src="04-poi-layers.png"
                                             title="Couches POI activables · transport · culture · santé" /> },
    { from: s(275),   dur: s(30), comp: <Screenshot src="05-compare-radar.png"
                                             title="Mode comparaison · 16e vs 19e" /> },
    { from: s(305),   dur: s(25), comp: <Choices /> },
    { from: s(330),   dur: s(10), comp: <Outro /> },
];

export const durationInFrames = SCENES[SCENES.length - 1].from
    + SCENES[SCENES.length - 1].dur;

export const UrbanDataExplorerDemo: React.FC = () => {
    return (
        <AbsoluteFill style={{ backgroundColor: "#0b1020" }}>
            {SCENES.map((sc, i) => (
                <Sequence key={i} from={sc.from} durationInFrames={sc.dur}>
                    {sc.comp}
                </Sequence>
            ))}
        </AbsoluteFill>
    );
};
