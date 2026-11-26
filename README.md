[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/mannamemmna/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/mannamemmna/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

# THE DAILY LEDGER — Thursday 26 November 2026

One 1024×1024 front page summing up the world's news of Thursday 26 November 2026:
a drawn masthead, a crimson date band, a lead story with its own illustration, four
regional cards and a six-line digest. Dark newsprint ground, cream type, amber accents.

## What it shows

**Lead — United States · New York:** Macy's 100th parade postponed to Saturday
28 November; a nor'easter and a high-wind warning (gusts to 55 mph) grounded the giant
balloons, the first weather postponement in the parade's 100-year history.
*(AP, Reuters, New York Times, Axios, UPI)*

**Cards**

- **TRADE** — Tariffs on 14 trading partners: US proposes duties over "excess industrial
  capacity", up to 20% on China. *(Reuters, RNZ, SBS, Business Standard, Mathrubhumi)*
- **ASIA** — Kim orders wider tactical nukes: North Korea expands nuclear material output,
  KCNA reports. *(Reuters, KCNA via Sacramento Bee)*
- **EUROPE** — Kyiv hit by ballistic barrage: missiles strike a shopping centre and two
  buildings; Zelensky presses NATO. *(Reuters, Kyiv Independent, Ukrinform)*
- **MIDDLE EAST** — Tankers burn in Hormuz: Iran says two vessels hit mines in the strait
  and warns shipping. *(Reuters/Arab News, SBS, Gulf News, LBC)*

**Also on the day**

1. **EGYPT** — 31 killed in fuel-truck fire on Cairo Ring Road. *(Reuters, AP)*
2. **SPACE** — Hera finds a stadium-sized crater on asteroid Dimorphos. *(ESA, CNN, Ars Technica)*
3. **BANGLADESH** — Garment wage raised 36% to 17,000 taka after protests. *(AP, Reuters, AFP)*
4. **BRAZIL** — Floods and landslides kill at least 8 in the south. *(Xinhua/civil defence, CNN Brasil)*
5. **SAUDI ARABIA** — Houthi projectile hits Jazan port, coalition says. *(Arab News, Saudi SPA)*
6. **CULTURE** — Duran Duran guitarist Andy Taylor dies at 65. *(Reuters, family statement)*

Sources line on the page: REUTERS · AP · AFP · BBC · KYIV INDEPENDENT · ESA — cross-checked.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`generator.py` draws the image (Pillow, deterministic — no network, no RNG, no clock; the
date is a constant), and the Node entrypoint ships `entry.png` verbatim: it checks the PNG
signature, the 1 MiB ceiling and the 1024×1024 IHDR limits, copies the file to
`$MAKEFUN_OUTPUT_DIR/entry.png`, and reads the copy back to prove it is identical.

```sh
python3 generator.py            # redraw entry.png and output/entry.png
md5sum entry.png output/entry.png
```
