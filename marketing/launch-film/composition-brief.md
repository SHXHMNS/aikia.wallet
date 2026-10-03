# Hyperframes Composition Brief: aikia.wallet

## Objective
Create a flagship, immersive launch film for aikia.wallet: one day at a café, where ghost regulars become known members.

## Output
- Composition directory: `composition/`
- Rendered video: `brag.mp4`
- Format: landscape — 1920x1080, 30fps
- Duration: 24.5s

## Source Material
- Project root: `~/Desktop/aikia.wallet/` (blueprint documents; no app code)
- Primary files read: Master Blueprint, Launch Readiness Blueprint, Developer Blueprint (HTML)
- Product name: aikia.wallet (a new product from aikia.wrld)
- Strongest claim: "The black card for every café."
- Key UI to recreate: the cover's wallet pass (Café Noor · CHROME MEMBER · Aarav Shah · ₹1,840 · Flat white, oat · 6 mornings · 7/9 stamps · "2 visits to your free cup") and the lock-screen nudge
- Copy that must appear verbatim (from the blueprint):
  - "Café Noor · 120 m away" / "Morning, Aarav. Your flat white is on us until 11."
  - "The black card for every café."
  - "No app to download."
  - "Fill My Tables" / 45-minute offer
  - "Ink. Chrome. Hyper Pink." (tiers)
  - "A members' club." / "Not a loyalty program." (from "We do not sell a loyalty program. We sell a members' club")

## Creative Direction
- Tone preset: cinematic (with app-store cleanliness)
- Creative direction: the user asked for an immersive, unique, multi-million-dollar product film with scrub, ghost mode, Apple liquid glass and rare effects, light and dark backgrounds, and a human feel
- Interpretation: every effect carries meaning. Ghost echoes are unknown guests. Liquid glass is the phone surface (notification, scrubber knob, Fill button, outro lens). Scrub is time of day. Handwriting and a thumb make it human.
- Hook: ghosts drift past; "Every café has regulars." plus a handwritten "almost none know who they are."
- Outro: "aikia.wallet" + "A members' club. Not a loyalty program."
- Avoid: generic SaaS language, abstract filler, invented numbers or claims

## Visual Identity
- Light: `#F5F6FA` / `#ECEEF5`; Dark: `#14111F` / `#1A1627`; Accent `#FF3D9A`; Lilac `#A98BFF`; Ice `#7FE7F2`
- Text: `#14111F` on light, `#F8F9FD` on dark
- Fonts: Dela Gothic One (display), Hanken Grotesk (body), Martian Mono (labels), Caveat (handwriting, registry font)
- References: the pass, nudge, 8-petal chrome mark, tier chip chrome gradient

## Storyboard
See `brag-plan.md`. Scenes: Ghosts 0–4.39 · Halo 4.39–8.74 · Black card 8.74–13.11 · Scrub 13.11–18.56 · Status 18.56–21.28 · Outro 21.28–24.5

## Audio
- Music: `assets/music/happy-beats-business-moves-vol-12-by-ende-dot-app.mp3`, trimmed and faded into `assets/music/bed.m4a` (a 1.5s fade-out), at volume 0.36
- Cues: `assets/music/cues/happy-beats-business-moves-vol-12-by-ende-dot-app.music-cues.json`. Locks: 8.74, 13.11, 18.56 (+22.37 tagline); beat grid 15.29–16.93 for the member cascade
- Audio-reactive: subtle bass → ambient glow scale/opacity and the pass rim light. Data is pre-extracted to `audio-data.js`.
- SFX: low-HF picks from `sfx-analysis.md`; exact picks are chosen after the animation exists
- Implementation: monolithic `index.html` with one paused GSAP timeline. Registry primitives were studied (echo-trail, gloss-sweep, grain-overlay, hw-path-text, liquid-glass blocks); the liquid glass is implemented DOM-native with an SVG displacement `backdrop-filter` (verified in capture) rather than the HTML-in-canvas blocks.
