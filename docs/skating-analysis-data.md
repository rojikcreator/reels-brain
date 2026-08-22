# Skating clubs — dátová analýza (624 reels z 33 klubov, IG feed metadata 2026-07-27)

Zdroj: play_count / like_count / comment_count / duration z prihláseného IG API. Medián (nie priemer — odolný voči výkyvom). Baseline medián pozretí všetkých 624 reels = **15 610**.

## A) Dĺžka videa vs. medián pozretí (MONOTÓNNY POKLES)
| Dĺžka | počet | medián pozretí |
|---|---|---|
| <10s | 61 | 22 395 |
| 10–20s | 121 | 21 893 |
| 20–40s | 195 | 16 840 |
| 40–90s | 187 | 12 023 |
| 90s+ | 60 | 9 719 |
→ Sub-20s reels majú ~2,3× medián pozretí oproti 90s+. Kratšie vyhráva jednoznačne.

## B) Typ obsahu vs. medián pozretí (index vs baseline 15 610)
| Kategória | počet | medián pozretí | index | medián ❤ |
|---|---|---|---|---|
| **Elitný/olympijský skater** (meno hviezdy, olympionik, majster) | 90 | **44 908** | **2,88×** | 1 632 |
| Emoji-only / minimálny caption (nechá skating hovoriť) | 106 | 22 201 | 1,42× | 626 |
| Element/technika (skok, piruéta, lift, side-by-side) | 48 | 21 937 | 1,41× | 946 |
| Hype/countdown (pred súťažou/šou) | 22 | 16 524 | 1,06× | 792 |
| Súťaž/competition | 110 | 14 889 | 0,95× | 706 |
| Nábor/tickets/club-biz | 28 | 12 310 | 0,79× | 289 |
| **BTS/tréning/day-in-life** (NAJČASTEJŠÍ obsah) | 116 | 11 590 | **0,74×** | 470 |
| Show/gala/on-ice | 43 | 10 504 | 0,67× | 212 |
→ KĽÚČ: najviac postovaná kategória (BTS/day-in-life) je POD priemerom. Elitný skater je 2,9× a je pod-produkovaný. Menej textu = viac dosahu.

## C) Rebríček klubov podľa mediánu pozretí (konzistencia)
| Klub | n | medián V | max V | medián ❤ | eng% (medL/medV) |
|---|---|---|---|---|---|
| helsinkirockettes | 52 | 55 873 | 482 261 | 1 959 | 3,5% |
| iceacademyofmontreal | 16 | 54 923 | 2 120 088 | 2 301 | 4,2% |
| kinoshita_skate_academy | 19 | 38 767 | 193 650 | 1 042 | 2,7% |
| teamuniquehsk | 28 | 29 545 | 360 552 | 1 195 | 4,0% |
| marigoldiceunity | 34 | 28 112 | 1 151 931 | 1 075 | 3,8% |
| angelsofplushenko | 64 | 26 451 | 180 432 | 754 | 2,9% |
| skatingschool (Champéry/Lambiel) | 18 | 23 728 | 135 012 | 1 082 | 4,6% |
| skatingclubbos | 24 | 20 819 | 1 741 374 | 531 | 2,6% |
| teamcricketofficial | 34 | 20 040 | 792 903 | 743 | 3,7% |
| miamioh_skating | 20 | 18 842 | 255 241 | 735 | 3,9% |
| lessupremes | 14 | 17 848 | 145 683 | 865 | 4,8% |
| haydenettesusa | 27 | 16 246 | 132 209 | 706 | 4,3% |
| valleybaysynchro | 33 | 15 610 | 256 691 | 978 | **6,3%** (najvyššia miera zapojenia) |
| nexxicesr | 26 | 12 805 | 27 647 | 469 | 3,7% |
(dolná tretina: toronto, chukyo, dscclub, wiener, dream.detroit, crystallettes, skatemariposa, csglyon, doshisha — medián <11k, väčšinou menej reels alebo dlhé/klubové videá)

## D) TOP 18 reels naprieč všetkými klubmi
1. 2 120k — @iceacademyofmontreal, 115s — ice dance practice "Leave a Light On" (Fabbri/Ayer, elit)
2. 1 741k — @skatingclubbos, 42s — Alysa Liu + olympionici (Naumov, Chan, Howe)
3. 1 152k — @marigoldiceunity, 11s — návrat na ľad pred sezónou
4. 793k — @teamcricketofficial, 8s — "side by side 3Lo" (element, ultra-krátke)
5. 597k — @skatingclubbos, 59s — Alysa Liu "Stateside"
6. 574k — @marigoldiceunity, 24s — competition week, mieria do Bostonu
7. 568k — @marigoldiceunity, 11s — emoji-only (❤️‍🔥)
8. 482k — @helsinkirockettes, 28s — "last reps on home ice"
9. 475k — @helsinkirockettes, 63s — "final 5-minute countdown to showtime"
10. 361k — @teamuniquehsk, 13s — emoji-only 🖤
11. 351k — @iceacademyofmontreal, 56s — "Flamenco with a Twist" Chock/Bates (matador koncept)
12. 331k — @wienereislaufverein, 10s — maskot comedy "Wo geht Karl hin?" (0,8k ❤ = obrovský dosah, nízke zapojenie)
13. 322k — @iceacademyofmontreal, 70s — "Who says you can't flamenco on ice" Chock/Bates
14. 257k — @valleybaysynchro, 21s — Alysa Liu dance party pred free skate
15. 255k — @miamioh_skating, 27s — "24× U.S. SYNCHRO CHAMPS"
16. 255k — @teamcricketofficial, 34s — "Great moments…" final training
17. 254k — @torontocricketclub, 76s — Tessa Virtue návšteva
18. 244k — @helsinkirockettes, 20s — home ice

## Predbežné závery z dát
1. **Hviezda > všetko.** Prítomnosť známeho mena (olympionik/majster) = 2,9× medián. Aj malé kluby vystrelia, keď zaberú/otagujú hviezdu (skatingclubbos 1,7M vďaka Alysa Liu; toronto 254k vďaka Tessa Virtue).
2. **Kratšie a čistejšie.** <20s + jeden silný element (skok/lift/side-by-side) alebo emoji-only caption prekonáva dlhé zostrihy a BTS.
3. **BTS je pasca.** Najčastejšie postované, ale pod priemerom — kluby míňajú úsilie na obsah, ktorý necestuje.
4. **Comedy/relatable** (maskot, "keď…") robí masívny reach aj s nízkym zapojením — dobré na dosah, nie na komunitu.
5. **Konzistencia:** helsinkirockettes a angelsofplushenko dokazujú, že pravidelný krátky formát drží vysoký medián; valleybaysynchro má najvyššiu mieru zapojenia (6,3%).
