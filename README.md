# The World Today — Sunday 22 November 2026

Entry for the make.fun bounty
[Sum up 22 November's world news in one image](https://make.fun/bounty/news-image-20261122)
(`news-image-20261122`).

## What it is

`main.py` is a pure Python 3.13 standard-library program. It draws a
1024x1024 newspaper-style front page — masthead, lead story, five story
cards and a briefs column — with a built-in 5x7 bitmap font and a
hand-written PNG encoder, and writes it to `/output/entry.png`
(`$MAKEFUN_OUTPUT_DIR` stands in for `/output` outside the grader).
No network, no clock, no randomness: every run writes identical bytes.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## The day's stories

All six stories were reported on Sunday 22 November 2026:

1. **Climate — COP31, Antalya.** The UN climate summit enters a second
   day of overtime, deadlocked over fossil fuels. (SBS, One Turn)
2. **Middle East — Bahrain.** Iran strikes an industrial site in Bahrain;
   two oil tankers are hit near the Strait of Hormuz. (Bahrain / IRGC /
   UK maritime agency)
3. **Justice — Mexico.** Mexican forces capture cartel boss Fausto Isidro
   Meza Flores, "El Chapo Isidro"; 11 killed in the operation. (DOJ, AP)
4. **War in Europe — Baltic / Ukraine.** A Russian cargo ship is hit by a
   drone in the Baltic Sea; Russia strikes Kryvyi Rih. (SBS, One Turn)
5. **Economy — Brussels.** The EU and Indonesia sign a trade deal after
   ten years of talks. (Reuters, European Commission)
6. **Disaster — Nigeria.** A boat carrying funeral mourners capsizes in
   Bayelsa State; 24 dead, 24 rescued. (Reuters, AP, NEMA)

In brief: a fire at the Hartha power station in Iraq kills 4; the FBI
confirms its NCIC crime database was breached.

## Files

- `main.py` — the program (draws the image, writes the PNG)
- `LICENSE` — MIT
- `README.md` — this file
- `.makefun/owner.json` — claim file naming the entrant's wallet
