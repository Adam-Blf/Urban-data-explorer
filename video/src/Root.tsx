import { Composition } from "remotion";
import { UrbanDataExplorerDemo, durationInFrames, FPS } from "./video/Composition";

export const Root: React.FC = () => {
    return (
        <Composition
            id="UrbanDataExplorerDemo"
            component={UrbanDataExplorerDemo}
            durationInFrames={durationInFrames}
            fps={FPS}
            width={1920}
            height={1080}
        />
    );
};
