/**
 * /linkedin-carousel starter — GenX-IT engineering aesthetic, code-rendered slides.
 *
 * 1080x1350 portrait. Rendered to PNG via Remotion stills (fps=1, one frame per
 * slide), then compiled to a single PDF for a LinkedIn Document post.
 *
 * Register in Root.tsx as a composition (see SKILL.md), then:
 *   for each i: npx remotion still Carousel out/carousel/slide-0{i+1}.png --frame={i}
 *
 * Edit the SLIDES array for your article. Copy MUST be routed through
 * knowledge/me/voice.md + the title rule first (see SKILL.md guardrails) — never
 * paste raw article or external-tool phrasing.
 *
 * Reusable patterns provided: TerminalAlert, TwoCol, DependencyStack, GrepBlock,
 * VerifierFlow, CtaPanel. Compose slides from these — they ARE the design system.
 */
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/FiraCode";

const { fontFamily: INTER } = loadInter();
const { fontFamily: MONO } = loadMono();

// ── design tokens (GitHub-dark, GenX-IT). Change palette in ONE place. ───────
const C = {
  bg: "#0D1117",
  text: "#FFFFFF",
  muted: "#8B949E",
  border: "#30363D",
  panel: "#161B22",
  orange: "#FF7B72", // system-alert
  yellow: "#E3B341", // firewall
  green: "#3FB950",
};
const W = 1080;
const H = 1350;
const PAD = 84;

// total slide count — set to match your deck (8 or 9). Used in the counter + footer.
const COUNT = 8;

export const Frame: React.FC<{
  no: number;
  children: React.ReactNode;
  cmd?: string;
  brand?: string;
}> = ({ no, children, cmd = "rskiles@enterprise:~$", brand = "THE STEEL AND THE SERVER ROOM" }) => (
  <AbsoluteFill style={{ backgroundColor: C.bg, fontFamily: INTER }}>
    <div style={{ position: "absolute", top: PAD - 30, left: PAD, right: PAD, display: "flex", justifyContent: "space-between", fontFamily: MONO, fontSize: 26, color: C.muted }}>
      <span>{cmd}</span>
      <span>[ {String(no).padStart(2, "0")} / {String(COUNT).padStart(2, "0")} ]</span>
    </div>
    <AbsoluteFill style={{ padding: `${PAD + 40}px ${PAD}px ${PAD + 30}px`, justifyContent: "center" }}>
      {children}
    </AbsoluteFill>
    <div style={{ position: "absolute", bottom: PAD - 36, left: PAD, right: PAD, borderTop: `1px solid ${C.border}`, paddingTop: 18, display: "flex", justifyContent: "space-between", fontFamily: MONO, fontSize: 24, color: C.muted }}>
      <span>{brand}</span>
      <span>{no < COUNT ? "swipe →" : "link in comments"}</span>
    </div>
  </AbsoluteFill>
);

const Dot: React.FC<{ color: string; size?: number }> = ({ color, size = 22 }) => (
  <span style={{ width: size, height: size, borderRadius: "50%", background: color, display: "inline-block" }} />
);

export const Panel: React.FC<{ children: React.ReactNode; style?: React.CSSProperties; accent?: string }> = ({
  children,
  style,
  accent = C.border,
}) => (
  <div style={{ background: C.panel, border: `1px solid ${accent}`, borderRadius: 12, padding: 34, ...style }}>{children}</div>
);

const H1: React.CSSProperties = { fontWeight: 800, fontSize: 84, lineHeight: 1.04, letterSpacing: "-0.02em", color: C.text };
const SUB: React.CSSProperties = { fontSize: 40, color: C.muted, marginTop: 26, lineHeight: 1.3 };
const TAG: React.CSSProperties = { fontFamily: MONO, fontSize: 26, color: C.orange, letterSpacing: "0.08em" };

// ── reusable slide PATTERNS (compose slides from these) ──────────────────────

// red [LABEL] alert block — use for the Hook / crisis moments.
export const TerminalAlert: React.FC<{ label: string; color?: string }> = ({ label, color = C.orange }) => (
  <Panel accent={color} style={{ marginBottom: 46 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 18, fontFamily: MONO, fontSize: 30, color: C.text }}>
      <Dot color={color} /> [{label}]
    </div>
  </Panel>
);

// left/right comparative boxes — use for The Chaos.
export const TwoCol: React.FC<{ left: [string, string]; right: [string, string] }> = ({ left, right }) => (
  <div style={{ display: "flex", gap: 24, marginTop: 50 }}>
    <Panel style={{ flex: 1 }}>
      <div style={{ fontFamily: MONO, fontSize: 24, color: C.yellow }}>{left[0]}</div>
      <div style={{ fontSize: 34, color: C.text, marginTop: 14 }}>{left[1]}</div>
    </Panel>
    <Panel style={{ flex: 1 }} accent={C.orange}>
      <div style={{ fontFamily: MONO, fontSize: 24, color: C.orange }}>{right[0]}</div>
      <div style={{ fontSize: 34, color: C.text, marginTop: 14 }}>{right[1]}</div>
    </Panel>
  </div>
);

// dependency tower with ONE load-bearing block highlighted — Root Cause slide.
export const DependencyStack: React.FC<{ items: string[]; hot: string; note?: string }> = ({ items, hot, note = "← pulled, undisclosed" }) => (
  <div style={{ marginTop: 40, display: "flex", flexDirection: "column", gap: 12 }}>
    {items.map((l) => {
      const isHot = l === hot;
      return (
        <div key={l} style={{ fontFamily: MONO, fontSize: 30, letterSpacing: "0.06em", color: isHot ? C.bg : C.text, background: isHot ? C.orange : C.panel, border: `1px solid ${isHot ? C.orange : C.border}`, borderRadius: 8, padding: "18px 26px", fontWeight: isHot ? 700 : 400 }}>
          {l} {isHot && `  ${note}`}
        </div>
      );
    })}
  </div>
);

// terminal command + result — use for "AI can't ask what nobody documented".
export const GrepBlock: React.FC<{ cmd: string; result: string }> = ({ cmd, result }) => (
  <Panel style={{ marginTop: 40, fontFamily: MONO, fontSize: 30, lineHeight: 1.8 }}>
    <div style={{ color: C.green }}>{cmd}</div>
    <div style={{ color: C.orange }}>{result}</div>
  </Panel>
);

// AI assists → Humans approve → Safe production — the Verifier slide.
export const VerifierFlow: React.FC = () => (
  <Panel style={{ marginTop: 40 }}>
    <div style={{ fontFamily: MONO, fontSize: 30, color: C.muted, display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
      <span style={{ color: C.yellow }}>AI assists</span><span>➔</span>
      <span style={{ color: C.green }}>Humans approve</span><span>➔</span>
      <span style={{ color: C.text }}>Safe production</span>
    </div>
  </Panel>
);

// lead-magnet CTA. ctaComment defaults to the first-comment technique.
export const CtaPanel: React.FC<{ magnet: string; ctaComment?: string }> = ({ magnet, ctaComment = "link in comments" }) => (
  <Panel accent={C.yellow} style={{ marginTop: 28 }}>
    <div style={{ fontSize: 36, fontWeight: 700, color: C.text }}>→ {magnet}</div>
    <div style={{ fontFamily: MONO, fontSize: 26, color: C.yellow, marginTop: 10 }}>{ctaComment}</div>
  </Panel>
);

const Hd: React.FC<{ tag?: string; children: React.ReactNode; color?: string }> = ({ tag, children, color = C.text }) => (
  <>
    {tag && <div style={TAG}>// {tag}</div>}
    <div style={{ ...H1, marginTop: tag ? 20 : 0, color }}>{children}</div>
  </>
);

// ── SLIDES — EDIT FOR YOUR ARTICLE (this example = ART3 reference) ────────────
const SLIDES: React.FC[] = [
  () => (<Frame no={1}><TerminalAlert label="CRITICAL_SYSTEM_FAULT" /><Hd>Your 5-word hook here</Hd><div style={{ ...SUB, fontStyle: "italic" }}>One-line setup.</div></Frame>),
  () => (<Frame no={2}><Hd tag="THE IMPOSSIBLE ORDER">The directive.</Hd><TwoCol left={["DIRECTIVE", "When."]} right={["CONDITIONS", "What made it insane."]} /></Frame>),
  () => (<Frame no={3}><Hd tag="THE EVACUATION">Setup line.</Hd><Panel accent={C.orange} style={{ marginTop: 44 }}><div style={{ fontSize: 48, fontWeight: 700, color: C.orange }}>The stakes.</div></Panel></Frame>),
  () => (<Frame no={4}><Hd tag="THE SCRAMBLE">You were ready.</Hd><div style={{ ...SUB, marginTop: 18 }}>The world was not.</div></Frame>),
  () => (<Frame no={5}><div style={TAG}>// THE REAL DISASTER</div><Hd>The real failure wasn't technical.</Hd></Frame>),
  () => (<Frame no={6}><Hd tag="ROOT CAUSE" color={C.orange}>Who actually broke it.</Hd><div style={{ ...SUB }}>The undisclosed change.</div><DependencyStack items={["DNS", "ACTIVE DIRECTORY", "CHANGE CONTROL", "NETWORK BACKBONE", "SERVICE ACCOUNTS", "BACKUPS"]} hot="NETWORK BACKBONE" /></Frame>),
  () => (<Frame no={7}><Hd tag="THE UNDOCUMENTED">The unreplaceable skill.</Hd><GrepBlock cmd={'$ grep -r "why_this_matters" ./legacy/'} result="> 0 results. no documentation found." /><div style={{ ...SUB, marginTop: 36, color: C.text, fontSize: 42 }}>AI can't ask what nobody documented.</div></Frame>),
  () => (<Frame no={8}><Hd tag="THE LESSON">The payoff (P1/P3 reframe).</Hd><div style={{ ...SUB, marginTop: 16, color: C.text }}>The empowering takeaway.</div><VerifierFlow /><CtaPanel magnet="The Steel and The Server Room" /></Frame>),
];

export const Carousel: React.FC = () => {
  const frame = useCurrentFrame();
  const Slide = SLIDES[Math.min(frame, SLIDES.length - 1)];
  return <Slide />;
};

export const CAROUSEL_DIMS = { W, H, COUNT: SLIDES.length };
