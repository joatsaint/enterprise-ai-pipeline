/**
 * /video-explainer starter composition.
 *
 * Proven, full-spec 5-scene educational explainer (1080x1920, 30fps, ~30s).
 * Copy this into a scaffolded Remotion project's src/Composition.tsx and edit
 * the five SCENE components for your topic. Keep the helpers as-is.
 *
 * To adapt to a new topic: change copy in SceneHook/SceneGoal/SceneLoop/
 * SceneTools/ScenePayoff. The PAYOFF must land an on-niche reframe for the
 * senior-IT / AI-era audience (a P1 "will AI replace me" or P3 "layoff" beat) —
 * never end on a generic "thanks for watching".
 *
 * Root.tsx must set: durationInFrames = 5*SCENE - 4*TRANS, width 1080, height 1920, fps 30.
 */
import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  random,
} from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont();

// ── BRAND CONFIG — palette TBD, change in ONE place ─────────────────────────
const COLORS = {
  bg: "#0a0a0a",
  text: "#ffffff",
  accent: "#6366f1", // indigo
  success: "#22c55e", // green
  muted: "#94a3b8",
};

const SCENE = 192; // frames per scene
const TRANS = 12; // cross-fade frames between scenes

// ── reusable helpers (do not rewrite per topic) ─────────────────────────────

const SafeZone: React.FC<{ children: React.ReactNode; bg?: string }> = ({
  children,
  bg = COLORS.bg,
}) => (
  <AbsoluteFill style={{ backgroundColor: bg }}>
    <AbsoluteFill
      style={{
        paddingTop: 150, // safe zone: platform status bar / search
        paddingBottom: 170, // safe zone: nav / swipe-up UI
        paddingLeft: 60,
        paddingRight: 60,
        justifyContent: "center",
        alignItems: "center",
        fontFamily,
      }}
    >
      {children}
    </AbsoluteFill>
  </AbsoluteFill>
);

const SpringIn: React.FC<{
  delay?: number;
  from?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ delay = 0, from = 40, children, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 200 } });
  return (
    <div
      style={{
        opacity: s,
        transform: `translateY(${interpolate(s, [0, 1], [from, 0])}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

const CountUp: React.FC<{
  to: number;
  delay?: number;
  durationInFrames?: number;
  suffix?: string;
  style?: React.CSSProperties;
}> = ({ to, delay = 0, durationInFrames = 40, suffix = "", style }) => {
  const frame = useCurrentFrame();
  const v = Math.round(
    interpolate(frame - delay, [0, durationInFrames], [0, to], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );
  return (
    <span style={{ fontVariantNumeric: "tabular-nums", ...style }}>
      {v}
      {suffix}
    </span>
  );
};

// Self-drawing SVG path via stroke-dashoffset. Pass the path length in `len`.
const DrawPath: React.FC<{
  d: string;
  len: number;
  delay?: number;
  durationInFrames?: number;
  stroke: string;
  strokeWidth?: number;
  fill?: string;
}> = ({
  d,
  len,
  delay = 0,
  durationInFrames = 30,
  stroke,
  strokeWidth = 6,
  fill = "none",
}) => {
  const frame = useCurrentFrame();
  const offset = interpolate(frame - delay, [0, durationInFrames], [len, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <path
      d={d}
      fill={fill}
      stroke={stroke}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeDasharray={len}
      strokeDashoffset={offset}
    />
  );
};

// Crisp filled arrowhead (use instead of emoji / stroked chevrons).
const ArrowHead: React.FC<{ x: number; y: number; angle: number; delay: number; color: string }> = ({
  x,
  y,
  angle,
  delay,
  color,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 200 } });
  return (
    <g transform={`translate(${x},${y}) rotate(${angle}) scale(${s})`} opacity={s}>
      <path d="M -14 -11 L 6 0 L -14 11 Z" fill={color} />
    </g>
  );
};

// Inline SVG icons (replace emoji — render consistently across machines).
const Icon: React.FC<{ name: "search" | "code" | "file"; color: string }> = ({ name, color }) => {
  const common = { fill: "none", stroke: color, strokeWidth: 3, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  if (name === "search")
    return (
      <svg width={36} height={36} viewBox="0 0 24 24" {...common}>
        <circle cx={10} cy={10} r={6} />
        <line x1={15} y1={15} x2={21} y2={21} />
      </svg>
    );
  if (name === "code")
    return (
      <svg width={36} height={36} viewBox="0 0 24 24" {...common}>
        <polyline points="8 7 3 12 8 17" />
        <polyline points="16 7 21 12 16 17" />
      </svg>
    );
  return (
    <svg width={36} height={36} viewBox="0 0 24 24" {...common}>
      <path d="M6 2 h8 l4 4 v16 h-12 z" />
      <line x1={9} y1={12} x2={15} y2={12} />
      <line x1={9} y1={16} x2={15} y2={16} />
    </svg>
  );
};

const H1: React.CSSProperties = { fontSize: 84, fontWeight: 800, color: COLORS.text, textAlign: "center", lineHeight: 1.05, letterSpacing: "-0.02em" };
const BODY: React.CSSProperties = { fontSize: 40, fontWeight: 400, color: COLORS.muted, textAlign: "center", marginTop: 28 };
const LABEL: React.CSSProperties = { fontSize: 36, fontWeight: 600, color: COLORS.accent };

// ── SCENES — EDIT THESE PER TOPIC ───────────────────────────────────────────

const SceneHook: React.FC = () => {
  const frame = useCurrentFrame();
  const underline = interpolate(frame, [18, 40], [0, 560], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <SafeZone>
      <SpringIn>
        <div style={H1}>How AI agents</div>
        <div style={{ ...H1, color: COLORS.accent }}>actually work</div>
      </SpringIn>
      <div style={{ height: 8, width: underline, background: COLORS.success, borderRadius: 4, marginTop: 28 }} />
      <SpringIn delay={16} style={{ ...BODY, fontSize: 44, color: COLORS.text }}>in 30 seconds</SpringIn>
    </SafeZone>
  );
};

const SceneGoal: React.FC = () => (
  <SafeZone>
    <SpringIn><div style={LABEL}>STEP 1</div></SpringIn>
    <SpringIn delay={8} style={{ marginTop: 16 }}><div style={H1}>It starts with a goal</div></SpringIn>
    <svg width={360} height={360} style={{ marginTop: 50 }}>
      <DrawPath d="M 180 60 a 120 120 0 1 0 0.1 0" len={754} delay={20} durationInFrames={34} stroke={COLORS.muted} />
      <DrawPath d="M 180 105 a 75 75 0 1 0 0.1 0" len={471} delay={34} durationInFrames={28} stroke={COLORS.accent} />
      <DrawPath d="M 180 150 a 30 30 0 1 0 0.1 0" len={188} delay={46} durationInFrames={20} stroke={COLORS.success} strokeWidth={10} />
    </svg>
    <SpringIn delay={56} style={BODY}>You give it an objective — not step-by-step commands.</SpringIn>
  </SafeZone>
);

const Node: React.FC<{ x: number; y: number; label: string; delay: number; color: string }> = ({ x, y, label, delay, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 200 } });
  return (
    <g transform={`translate(${x},${y}) scale(${interpolate(s, [0, 1], [0.6, 1])})`} opacity={s}>
      <rect x={-110} y={-46} rx={20} width={220} height={92} fill="#14161c" stroke={color} strokeWidth={4} />
      <text textAnchor="middle" dominantBaseline="central" fill={COLORS.text} fontSize={38} fontWeight={700} fontFamily={fontFamily}>{label}</text>
    </g>
  );
};

const SceneLoop: React.FC = () => (
  <SafeZone>
    <SpringIn><div style={LABEL}>STEP 2</div></SpringIn>
    <SpringIn delay={8} style={{ marginTop: 16 }}><div style={H1}>It runs a loop</div></SpringIn>
    <svg width={760} height={620} style={{ marginTop: 30 }}>
      <DrawPath d="M 250 150 L 500 150" len={250} delay={40} stroke={COLORS.accent} />
      <DrawPath d="M 600 235 L 470 430" len={235} delay={52} stroke={COLORS.accent} />
      <DrawPath d="M 290 430 L 160 235" len={235} delay={64} stroke={COLORS.accent} />
      <ArrowHead x={505} y={150} angle={0} delay={50} color={COLORS.accent} />
      <ArrowHead x={468} y={433} angle={123} delay={62} color={COLORS.accent} />
      <ArrowHead x={158} y={232} angle={237} delay={74} color={COLORS.accent} />
      <Node x={180} y={150} label="Think" delay={16} color={COLORS.success} />
      <Node x={580} y={150} label="Act" delay={28} color={COLORS.success} />
      <Node x={380} y={460} label="Observe" delay={40} color={COLORS.success} />
    </svg>
    <SpringIn delay={80} style={BODY}>Reason, take an action, check the result — repeat.</SpringIn>
  </SafeZone>
);

const ToolChip: React.FC<{ icon: "search" | "code" | "file"; label: string; delay: number }> = ({ icon, label, delay }) => (
  <SpringIn delay={delay} from={30}>
    <div style={{ display: "flex", alignItems: "center", gap: 14, background: "#14161c", border: `3px solid ${COLORS.accent}`, borderRadius: 16, padding: "18px 26px", fontSize: 34, fontWeight: 600, color: COLORS.text }}>
      <Icon name={icon} color={COLORS.accent} />
      {label}
    </div>
  </SpringIn>
);

const SceneTools: React.FC = () => (
  <SafeZone>
    <SpringIn><div style={LABEL}>STEP 3</div></SpringIn>
    <SpringIn delay={8} style={{ marginTop: 16 }}><div style={H1}>It uses tools</div></SpringIn>
    <div style={{ display: "flex", gap: 28, marginTop: 56, justifyContent: "center", flexWrap: "wrap" }}>
      <ToolChip icon="search" label="Search" delay={22} />
      <ToolChip icon="code" label="Code" delay={32} />
      <ToolChip icon="file" label="Files" delay={42} />
    </div>
    <SpringIn delay={60} style={{ marginTop: 70, textAlign: "center" }}>
      <div style={{ fontSize: 120, fontWeight: 800, color: COLORS.success }}>
        <CountUp to={100} delay={60} durationInFrames={46} suffix="+" />
      </div>
      <div style={{ ...BODY, marginTop: 4 }}>steps in a single run</div>
    </SpringIn>
  </SafeZone>
);

const Particles: React.FC = () => {
  const frame = useCurrentFrame();
  const { height, width } = useVideoConfig();
  return (
    <AbsoluteFill>
      {new Array(13).fill(0).map((_, i) => {
        const speed = 0.6 + random(`s${i}`) * 0.9;
        const y = height + 80 - ((frame * speed * 6 + random(`o${i}`) * height) % (height + 160));
        const r = 6 + random(`r${i}`) * 18;
        return (
          <div key={i} style={{ position: "absolute", left: random(`x${i}`) * width, top: y, width: r, height: r, borderRadius: "50%", background: i % 2 ? COLORS.accent : COLORS.success, opacity: 0.25 }} />
        );
      })}
    </AbsoluteFill>
  );
};

// PAYOFF: must reframe on-niche for the senior-IT / AI-era audience.
const ScenePayoff: React.FC = () => (
  <SafeZone>
    <Particles />
    <SpringIn>
      <div style={{ ...H1, fontSize: 76 }}>Agents don't</div>
      <div style={{ ...H1, fontSize: 76 }}>replace experts.</div>
    </SpringIn>
    <SpringIn delay={18} style={{ marginTop: 36 }}>
      <div style={{ ...H1, fontSize: 60, color: COLORS.success }}>They run your playbook —</div>
      <div style={{ ...H1, fontSize: 60, color: COLORS.success }}>faster.</div>
    </SpringIn>
    <SpringIn delay={40} style={{ ...BODY, fontSize: 38, marginTop: 48 }}>Be the one who runs them.</SpringIn>
  </SafeZone>
);

// ── root ────────────────────────────────────────────────────────────────────

export const MyComposition: React.FC = () => {
  const timing = linearTiming({ durationInFrames: TRANS });
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={SCENE}><SceneHook /></TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={timing} />
      <TransitionSeries.Sequence durationInFrames={SCENE}><SceneGoal /></TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={timing} />
      <TransitionSeries.Sequence durationInFrames={SCENE}><SceneLoop /></TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={timing} />
      <TransitionSeries.Sequence durationInFrames={SCENE}><SceneTools /></TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={timing} />
      <TransitionSeries.Sequence durationInFrames={SCENE}><ScenePayoff /></TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
