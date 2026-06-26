/**
 * TextCard — full 9:16 (1080×1920) background composition for Randy's YouTube Shorts.
 *
 * Layout:
 *   - Dark background (#0C0C0E) fills the full 9:16 frame
 *   - Text content rendered in the TOP 50% (y=0 to ~960) — avatar occupies bottom half
 *   - Text hook overlay: upper area, first 10 seconds
 *   - Section cards: slide up + fade in at Whisper-timed boundaries
 *   - Gradient fade at y=800 so content blends naturally into the avatar zone
 *   - Brand accent line at the frame midpoint (y=960) — subtle divider
 *
 * Brand colors: neon green (#39ff14), orange (#FF6700), white (#f8f9fa)
 */
import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import data from "../public/data.json";

type Section = {
  label:      string;
  text:       string;
  startFrame: number;
  endFrame:   number;
  color:      string;
  size:       string;
};

type Data = typeof data;

const FONT_SIZES: Record<string, number> = {
  large:  80,
  medium: 58,
  small:  44,
};

// Text renders in the top safe zone — below the hook, above the avatar
const SAFE_TOP = 260;
const SAFE_BOTTOM = 880;   // avatar starts at ~y=960; leave breathing room

const SectionCard: React.FC<{ section: Section; frame: number; fps: number }> = ({
  section,
  frame,
  fps,
}) => {
  const isActive = frame >= section.startFrame && frame < section.endFrame;
  if (!isActive) return null;

  const localFrame = frame - section.startFrame;
  const slideY = spring({ frame: localFrame, fps, config: { damping: 14, stiffness: 120 } });
  const opacity = interpolate(localFrame, [0, 12], [0, 1], { extrapolateRight: "clamp" });

  const fontSize = FONT_SIZES[section.size] ?? 58;
  const charsPerLine = section.size === "large" ? 16 : 22;

  const words = section.text.split(" ");
  const lines: string[] = [];
  let line = "";
  for (const word of words) {
    if ((line + " " + word).trim().length > charsPerLine && line) {
      lines.push(line.trim());
      line = word;
    } else {
      line = (line + " " + word).trim();
    }
  }
  if (line) lines.push(line.trim());

  const availableHeight = SAFE_BOTTOM - SAFE_TOP;

  return (
    <div
      style={{
        position: "absolute",
        top: SAFE_TOP,
        left: 60,
        right: 60,
        height: availableHeight,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        transform: `translateY(${(1 - slideY) * 50}px)`,
        opacity,
      }}
    >
      <div
        style={{
          textAlign: "center",
          fontFamily: "Arial Black, Impact, Arial, sans-serif",
          fontWeight: 900,
          color: section.color,
          textShadow: "0 2px 20px rgba(0,0,0,0.95), 0 0 40px rgba(0,0,0,0.7)",
          lineHeight: 1.15,
        }}
      >
        {lines.map((l, i) => (
          <div key={i} style={{ fontSize, marginBottom: 10 }}>
            {l.toUpperCase()}
          </div>
        ))}
      </div>
    </div>
  );
};

const TextHookOverlay: React.FC<{
  text:     string;
  endFrame: number;
  frame:    number;
  fps:      number;
}> = ({ text, endFrame, frame, fps }) => {
  if (frame > endFrame) return null;

  const fadeIn  = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [endFrame - 15, endFrame], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <div
      style={{
        position: "absolute",
        top: 60,
        left: 50,
        right: 50,
        textAlign: "center",
        opacity,
        fontFamily: "Arial, sans-serif",
        fontWeight: 700,
        fontSize: 40,
        color: "#ffffff",
        textShadow: "0 2px 16px rgba(0,0,0,0.95)",
        letterSpacing: "0.03em",
        lineHeight: 1.3,
      }}
    >
      {text.toUpperCase()}
    </div>
  );
};

// Gradient fade at the avatar boundary — top layer blends into avatar below
const AvatarBlend: React.FC = () => (
  <div
    style={{
      position: "absolute",
      top: 760,
      left: 0,
      right: 0,
      height: 300,
      background: "linear-gradient(to bottom, transparent, #0C0C0E 80%)",
      pointerEvents: "none",
    }}
  />
);

// Subtle brand accent at the avatar midline
const MidlineAccent: React.FC<{ frame: number }> = ({ frame }) => {
  const shift = (frame / 5) % 360;
  return (
    <div
      style={{
        position: "absolute",
        top: 956,
        left: 0,
        right: 0,
        height: 4,
        background: `linear-gradient(${shift}deg, #39ff14 0%, #FF6700 50%, #39ff14 100%)`,
        opacity: 0.6,
      }}
    />
  );
};

export const TextCard: React.FC<Data> = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: props.bgColor }}>
      {/* Section cards — in the top safe zone */}
      {props.sections.map((sec: Section) => (
        <SectionCard key={sec.label} section={sec} frame={frame} fps={fps} />
      ))}

      {/* Avatar blend gradient */}
      <AvatarBlend />

      {/* Text hook — top area, first N seconds */}
      <TextHookOverlay
        text={props.textHook}
        endFrame={props.textHookEndFrame}
        frame={frame}
        fps={fps}
      />

      {/* Animated midline accent */}
      <MidlineAccent frame={frame} />
    </AbsoluteFill>
  );
};
