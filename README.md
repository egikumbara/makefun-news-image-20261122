[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/egikumbara/makefun-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/egikumbara/makefun-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# The World Today — Sunday 22 November 2026

A newspaper front page that sums up the world's news of Sunday 22 November 2026 in one 1024×1024 PNG. Six stories, all first reported on that day:

1. **Gulf war widens** — Iran claims missile and drone strikes on two US Patriot air-defence radars at bases in Bahrain, as Houthi forces strike the Saudi capital and tankers are hit in the Gulf.
2. **COP31 nears a deal** — climate talks in Antalya table a new package in the early hours of Sunday; nearly 200 delegations hope to approve it later in the day.
3. **Peru shaken by a 6.9 quake** — a strong earthquake strikes Peru's Andes, with no deaths or major damage immediately reported.
4. **Trump backs a 10% card cap** — the president says he will work with Democrats to cap credit-card interest rates at 10%.
5. **Boat sinks in Nigeria** — at least 24 people die when an overloaded boat carrying mourners to a funeral capsizes in southern Nigeria.
6. **Brazil town clears rubble** — a deadly storm tears through a Brazilian town; residents clear the wreckage of their homes.

Plus a footer strip: Bitcoin rebounds after a two-year low, French protesters march for a sixth weekend over living costs, and Belgium faces an air-traffic shutdown in Monday's strike.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024×1024, under 1 MiB). The program is pure Python 3 standard library — a hand-rolled PNG writer and a hand-built 5×7 bitmap font — with no network, no clock and no randomness, so two runs produce byte-identical output. Run `python3 verify.py` to check determinism, size and dimensions.

## About

Entry for the [news-image-20261122 bounty on make.fun](https://make.fun/bounty/news-image-20261122). Licensed under the MIT License.
