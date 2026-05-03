# Vidéo de démo · Urban Data Explorer

Projet Remotion 4 (TypeScript / React) qui génère la vidéo de démonstration
de la soutenance · 1920×1080, 30 fps, ~5 min 40.

## Setup

```bash
cd video
npm install
```

## Studio interactif (live preview)

```bash
npm start
# → http://localhost:3000 · timeline + preview frame par frame
```

## Build vidéo MP4

```bash
npm run build
# → video/out/urban-data-explorer-demo.mp4
```

Build VP9/WebM (plus léger pour le web) ·

```bash
npm run build:webm
# → video/out/urban-data-explorer-demo.webm
```

## Structure

```
video/
├── package.json
├── tsconfig.json
├── remotion.config.ts
├── public/                        # assets servis via staticFile()
│   ├── efrei-logo-white.png
│   └── screenshots/02..05.png    # captures du dashboard live
└── src/
    ├── index.ts                   # registerRoot
    ├── Root.tsx                   # Composition declaration
    └── video/
        ├── Composition.tsx        # 12 scènes orchestrées
        ├── theme.ts               # palette dashboard
        ├── helpers.tsx            # useFadeIn, useSlideUp
        └── scenes/
            ├── Cover.tsx          [00:00 - 00:25]
            ├── Problem.tsx        [00:25 - 00:55]
            ├── Answer.tsx         [00:55 - 01:25]
            ├── Architecture.tsx   [01:25 - 02:00]
            ├── Terminal.tsx       [02:00 - 02:40]
            ├── Api.tsx            [02:40 - 03:10]
            ├── Screenshot.tsx     [×4 · 03:10 - 05:05]
            ├── Choices.tsx        [05:05 - 05:30]
            └── Outro.tsx          [05:30 - 05:40]
```

## Régénérer les screenshots

Si le dashboard évolue ·

```bash
cd ..
python scripts/capture_screenshots.py
cp docs/screenshots/0[2345]*.png video/public/screenshots/
```

## Audio (optionnel)

Le projet ne contient pas de piste audio par défaut. Pour ajouter une narration ·

1. Enregistrer la voix-off avec [Audacity](https://www.audacityteam.org/) en
   suivant le script `docs/DEMO_SCRIPT.md`.
2. Placer le `.mp3` dans `video/public/voiceover.mp3`.
3. Dans `Composition.tsx`, ajouter ·
   ```tsx
   import { Audio, staticFile } from "remotion";
   <Audio src={staticFile("voiceover.mp3")} />
   ```
4. Build music libre de droits suggérée · Kevin MacLeod (CC-BY).
