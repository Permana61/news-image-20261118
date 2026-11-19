# news-image

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Permana61/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Permana61/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A hand-drawn infographic summing up the world's news of Wednesday, 18 November 2026, in a single 1024×1024 image, built for make.fun's "Sum up 18 November's world news in one image" bounty ($250 in USDC). `main.py` is the whole entry: pure Python 3.13 standard library, no network, no randomness, no clock — it draws the masthead ("WORLD NEWS — WEDNESDAY 18 NOVEMBER 2026") and six panels with shape-drawn pictograms, headlines and one-line summaries, all text rendered in a built-in 5×7 bitmap font so it stays legible at ~300 px. The six stories, verified from AP, Reuters, BBC, Polygon and The Art Newspaper: Trump lands in China ahead of the Xi–Putin talks at APEC; Iran strikes a US base in Kuwait and sites in Bahrain (drones intercepted, no damage reported); Anthropic prices a record $81.3B IPO at a $1.5T valuation; Van Gogh's "Châtaigniers en Fleurs" sells for a record $190.4M at Sotheby's; GTA 6 reviews hit 99 on Metacritic; and Brazil's Senate approves Lula's $10B fiscal package. The repository holds code only — the image is drawn fresh on every run.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It needs Python 3.13 (standard library only) and writes `out/entry.png`. Running it twice produces byte-identical output.

---

<sub>Entered on [make.fun](https://make.fun/?ref=3zcdv8qs&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
