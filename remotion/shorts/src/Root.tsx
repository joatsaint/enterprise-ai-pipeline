import { Composition } from "remotion";
import { TextCard } from "./TextCard";
import data from "../public/data.json";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="TextCard"
        component={TextCard as any}
        durationInFrames={data.durationInFrames}
        fps={data.fps}
        width={data.width}
        height={data.height}
        defaultProps={data as any}
      />
    </>
  );
};
