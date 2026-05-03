import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

/** Fade-in opacity over `durationFrames` from frame 0. */
export const useFadeIn = (durationFrames = 18) => {
    const frame = useCurrentFrame();
    return interpolate(frame, [0, durationFrames], [0, 1], {
        extrapolateRight: "clamp",
    });
};

/** Spring-based slide-up + fade. */
export const useSlideUp = (delay = 0) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const k = spring({
        fps,
        frame: Math.max(0, frame - delay),
        config: { damping: 18, stiffness: 100 },
    });
    return {
        opacity: k,
        transform: `translateY(${(1 - k) * 24}px)`,
    };
};
