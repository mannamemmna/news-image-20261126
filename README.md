[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/badge/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/mannamemmna/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/mannamemmna/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

# THE DAILY LEDGER — Thursday 26 November 2026

One 1024×1024 front page summing up the world's news of Thursday 26 November 2026,
built as a classic LIGHT newsprint broadsheet: cream paper (#F4EFE3), black ink,
one red spot colour and a single accent blue. Masthead, oversized date line, a
lead story with a drawn ink-and-red scene, six ruled story columns and a
three-column "day in brief" strip of eighteen one-line items. No rounded cards,
no dark panels, no gradients; hairline rules on one strict grid.

## What it shows

**Lead — New York · the parade that waited:** Macy's 100th parade postponed to
Saturday 28 November. A nor'easter and a high-wind warning with gusts to 55 mph
grounded the giant balloons — the first weather postponement in its 100-year
history. It was halted only for WWII, 1942-44. The illustration is a flat black
skyline with cream lit windows, three red balloons heeling in the wind on sagging
tethers, diagonal rain and an umbrella crowd.

**Six columns**

- **TRADE** — US proposes tariffs on 14 trading partners: duties over what
  Washington calls structural excess industrial capacity; up to 20% on China,
  25% on India with 17% if a deal is struck; world stocks slid as the AI rally
  faded. *(Reuters, RNZ, SBS, Business Standard)*
- **ASIA** — Kim orders wider tactical nuclear deployment: Kim Jong Un inspected
  nuclear material production and weapons research facilities and said the country
  should deploy tactical nuclear weapons across multiple domains; KCNA reported
  the remarks on Thursday. *(Reuters, KCNA)*
- **EUROPE** — Kyiv hit by ballistic missiles: the strike late on Wednesday hit a
  shopping centre and two other buildings; three people were injured, one
  seriously; Zelensky pressed NATO on membership. *(Reuters, Kyiv Independent,
  Ukrinform)*
- **MIDDLE EAST** — Tankers burn in the Strait of Hormuz: Iran's Revolutionary
  Guards said an LNG carrier and an oil tanker caught fire after hitting naval
  mines; Tehran warned shipping to follow its instructions. *(Reuters/Arab News,
  SBS, Gulf News)*
- **AFRICA** — Egypt fire kills 31 on Cairo ring road: a vehicle carrying
  petroleum products overturned and caught fire; 21 people were wounded.
  *(Reuters, AP)*
- **SCIENCE** — Hera finds a stadium-sized crater on Dimorphos: ESA released the
  first images from its Hera probe, showing the crater left by NASA's 2022 DART
  impact across the asteroid's whole width; Dimorphos is tumbling. *(ESA, CNN,
  Ars Technica, Scientific American)*

**The day in brief** — eighteen one-line items tagged US, EU, ME, AF, AS, LA, CU
and SP across three ruled columns: birthright-citizenship order blocked again;
NVIDIA questioned by a Senate Democrat; Murmansk governor held; 34 countries on
riot gas; Italian priests report; Bulgaria's first migrant boat in months; Jazan
port hit; Syrian security personnel killed; Iran on a US naval blockade;
Bangladesh garment wage; Niger State killings; Kenya cult leader; Swiss envoy
expelled; 3,000-troop drills in Cambodia; Brazil floods; Ecuador–US review;
Andy Taylor dies; Sindarov–Gukesh game 2.

Sources line on the page: REUTERS · AP · AFP · BBC · KYIV INDEPENDENT · ESA · UPI ·
AL JAZEERA — every item cross-checked in two outlets.

## How it is built

`generator.py` plans before it paints: `plan()` measures every string with
`draw.textlength`, fixes every baseline on one strict grid, and the text and
layout audits re-check that same plan — the run refuses to save `entry.png`
if any string overflows its column or any band collides. Deterministic by
construction: the date is a constant, every coordinate is arithmetic, no random,
clock or network call; Pillow and the stdlib only.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

The Node entrypoint ships `entry.png` verbatim: it checks the PNG signature, the
1 MiB ceiling and the 1024×1024 IHDR limits, copies the file to
`$MAKEFUN_OUTPUT_DIR/entry.png`, and reads the copy back to prove it is identical.

```sh
python3 generator.py            # redraw entry.png and output/entry.png
md5sum entry.png output/entry.png
```
