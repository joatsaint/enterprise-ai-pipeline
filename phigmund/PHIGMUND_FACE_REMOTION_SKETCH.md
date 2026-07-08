# Phigmund Face — Remotion Component Sketch
**Status:** Design sketch. Not yet built. Use this to decide production tier before building.

---

## What Needs to Be True for Tier 1

Phigmund's face on screen needs:
1. A terminal/console aesthetic (dark background, green or amber text)
2. A visible "H" on the forehead area (small, silver)
3. Text output that appears line by line (typewriter effect)
4. Optional: minimal face geometry (eyes, expression) that fits the aesthetic

Remotion can do all of this with standard CSS animation. Zero external dependencies.

---

## Proposed Remotion Component Structure

```
remotion/
└── phigmund/
    ├── PhigmundFace.tsx        ← the main face component
    ├── TerminalOutput.tsx      ← typewriter text effect
    ├── CommandDeckUI.tsx       ← outer shell/chrome
    └── index.ts
```

---

## PhigmundFace.tsx Concept

```tsx
// PhigmundFace.tsx — Tier 1 implementation concept

import { useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';

// Phigmund's face is geometric, not photorealistic
// This fits both the aesthetic AND removes HeyGen credit dependency

export const PhigmundFace: React.FC<{
  expression: 'neutral' | 'observational' | 'analytical' | 'mildly_concerned'
}> = ({ expression }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // Subtle breathing animation — he's alive, but professionally so
  const breathe = Math.sin(frame / 30) * 2;
  
  // The H on his forehead — small, silver, always present
  const hOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  
  return (
    <div style={{
      width: 200,
      height: 250,
      background: '#0a0a0a',
      border: '1px solid #333',
      borderRadius: 8,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      fontFamily: 'monospace',
    }}>
      
      {/* The H — Red Dwarf callback */}
      <div style={{
        position: 'absolute',
        top: 20,
        fontSize: 14,
        color: '#c0c0c0',  // silver
        opacity: hOpacity,
        fontWeight: 'bold',
        letterSpacing: 1,
      }}>
        H
      </div>
      
      {/* Face geometry — minimal, terminal-style */}
      <div style={{
        marginTop: 45,
        fontSize: 48,
        transform: `translateY(${breathe}px)`,
        filter: expression === 'observational' ? 'brightness(1.2)' : 'brightness(1.0)',
      }}>
        {/* Expression map */}
        {expression === 'neutral' && '◉_◉'}
        {expression === 'observational' && '◉‿◉'}
        {expression === 'analytical' && '◈_◈'}
        {expression === 'mildly_concerned' && '◉_◈'}
      </div>
      
      {/* Status line */}
      <div style={{
        position: 'absolute',
        bottom: 15,
        fontSize: 9,
        color: '#555',
        letterSpacing: 0.5,
      }}>
        PHIGMUND v1.0 | OPERATIONAL
      </div>
      
    </div>
  );
};
```

---

## TerminalOutput.tsx Concept

```tsx
// TerminalOutput.tsx — typewriter effect for Phigmund's responses

import { useCurrentFrame } from 'remotion';

export const TerminalOutput: React.FC<{
  text: string;
  startFrame: number;
  charsPerFrame?: number;
}> = ({ text, startFrame, charsPerFrame = 2 }) => {
  const frame = useCurrentFrame();
  
  const charsToShow = Math.max(0, (frame - startFrame) * charsPerFrame);
  const visibleText = text.substring(0, charsToShow);
  
  return (
    <div style={{
      fontFamily: 'Courier New, monospace',
      fontSize: 14,
      color: '#00ff41',  // matrix green — or use '#ffb000' for amber
      background: '#0a0a0a',
      padding: '12px 16px',
      minHeight: 200,
      whiteSpace: 'pre-wrap',
      lineHeight: 1.6,
    }}>
      {visibleText}
      {/* Blinking cursor */}
      <span style={{
        animation: 'blink 1s step-end infinite',
        color: '#00ff41',
      }}>█</span>
    </div>
  );
};
```

---

## CommandDeckUI.tsx Concept

```tsx
// The outer shell — Command Deck chrome + scanlines for atmosphere

export const CommandDeckUI: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  return (
    <div style={{
      width: '100%',
      height: '100%',
      background: '#050505',
      border: '2px solid #1a3a1a',
      borderRadius: 4,
      boxShadow: '0 0 20px rgba(0, 255, 65, 0.1)',
      overflow: 'hidden',
      position: 'relative',
    }}>
      
      {/* Title bar */}
      <div style={{
        background: '#0f1f0f',
        padding: '6px 12px',
        fontSize: 11,
        color: '#00aa22',
        fontFamily: 'monospace',
        letterSpacing: 2,
        borderBottom: '1px solid #1a3a1a',
        display: 'flex',
        justifyContent: 'space-between',
      }}>
        <span>◈ COMMAND DECK</span>
        <span style={{ color: '#444' }}>PHIGMUND INTERFACE v1.0</span>
      </div>
      
      {/* Scanline overlay — subtle, atmospheric */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)',
        pointerEvents: 'none',
        zIndex: 10,
      }} />
      
      {children}
      
    </div>
  );
};
```

---

## Build Time Estimate

| Task | Time | Prerequisites |
|------|------|---------------|
| Create `remotion/phigmund/` component folder | 30 min | Remotion already installed |
| Build PhigmundFace.tsx | 45 min | None |
| Build TerminalOutput.tsx | 30 min | None |
| Build CommandDeckUI.tsx | 30 min | None |
| Wire up to existing Remotion setup | 20 min | Existing Remotion config |
| Test render first demo sequence | 30 min | All above |
| **Total** | **~3 hours** | Session with focus |

---

## What Randy Needs to Decide Before Building

1. **Color palette:** Matrix green (`#00ff41`) vs amber (`#ffb000`) vs custom?
2. **Face style:** ASCII art (`◉_◉`) vs SVG face vs no face (pure terminal)?
3. **The H:** How visible? Subtle (like Rimmer's — you have to know to look) vs obvious (glowing)?
4. **Randy's camera position** relative to the Command Deck screen — how much screen area?

None of these block building. They affect the vibe. Decide while the component builds.

---

## The Fastest Path to Pilot 1

If Randy wants to record Episode 1 as fast as possible:

**Skip this file.** Use a screenshare of the terminal instead.

Run `email_responder.py` in Windows Terminal. Full screen. Dark theme. Increase font size. Randy talks to the terminal window. Phigmund's text appears.

That's the simplest version. It still works. The face component adds atmosphere, not function. Add it after the pilot proves the format resonates.
