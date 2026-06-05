# National anthem MP3 files

Drop MP3 files in this folder to use real recordings instead of the synthesised fallback.

## Fastest workflow — nationalanthems.info

The site **https://nationalanthems.info** has free MP3 downloads of all national anthems. The recordings are of public-domain compositions, freely usable.

1. Visit the URL for the nation:
   - Switzerland: <https://nationalanthems.info/ch.htm>
   - Germany:     <https://nationalanthems.info/de.htm>
   - Singapore:   <https://nationalanthems.info/sg.htm>
   - USA:         <https://nationalanthems.info/us.htm>
   - France:      <https://nationalanthems.info/fr.htm>
   - General pattern: `https://nationalanthems.info/<iso-code>.htm`
2. Right-click the MP3 link → **Save target as…**
3. Save into this folder using the **ISO 2-letter code**:
   `ch.mp3`, `de.mp3`, `sg.mp3`, `us.mp3`, `fr.mp3`, …
4. Commit + push → Portainer "Pull and redeploy" with **☑ Re-pull image**
5. Done — the app picks it up automatically.

**No renaming needed** if you download from nationalanthems.info — their ISO codes match what the app looks for.

## Accepted filenames per nation

For each flag the app tries the ISO file first, then a long fallback name (lowercase):

| Flag | Try first | Fallback |
|---|---|---|
| 🇨🇭 Switzerland | `ch.mp3` | `switzerland.mp3` |
| 🇩🇪 Germany | `de.mp3` | `germany.mp3` |
| 🇺🇸 USA | `us.mp3` | `usa.mp3` |
| 🇫🇷 France | `fr.mp3` | `france.mp3` |
| 🇬🇧 UK | `gb.mp3` | `uk.mp3` |
| 🇮🇹 Italy | `it.mp3` | `italy.mp3` |
| 🇪🇸 Spain | `es.mp3` | `spain.mp3` |
| 🇧🇷 Brazil | `br.mp3` | `brazil.mp3` |
| 🇦🇷 Argentina | `ar.mp3` | `argentina.mp3` |
| 🇯🇵 Japan | `jp.mp3` | `japan.mp3` |
| 🇳🇱 Netherlands | `nl.mp3` | `netherlands.mp3` |
| 🇵🇹 Portugal | `pt.mp3` | `portugal.mp3` |
| 🇧🇪 Belgium | `be.mp3` | `belgium.mp3` |
| 🇸🇬 Singapore | `sg.mp3` | `singapore.mp3` |
| 🇦🇹 Austria | `at.mp3` | `austria.mp3` |
| 🇲🇽 Mexico | `mx.mp3` | `mexico.mp3` |
| 🇸🇪 Sweden | `se.mp3` | `sweden.mp3` |
| 🇵🇱 Poland | `pl.mp3` | `poland.mp3` |
| 🇳🇴 Norway | `no.mp3` | `norway.mp3` |
| 🇩🇰 Denmark | `dk.mp3` | `denmark.mp3` |
| 🇭🇷 Croatia | `hr.mp3` | `croatia.mp3` |
| 🇰🇷 South Korea | `kr.mp3` | `south-korea.mp3` |

## How playback works

The app fetches and decodes the file once, then **caches it in memory** for the rest of the page session. Re-plays are instant.

Only the **first 5 seconds** are played, with 0.15 s fade-in and 0.4 s fade-out. If no MP3 exists, the synth fallback runs.

## Diagnostics (F12 → Console)

- `[Anthem] Loaded /static/anthems/ch.mp3 (45.3s)` — real anthem playing
- `[Anthem] No MP3 for 🇨🇭 (tried: ch.mp3, switzerland.mp3), using synth` — fallback

## Trim long files (optional)

Most anthems on nationalanthems.info are 30–60 s. The app clips to 5 s on playback anyway, but if you want smaller files:

```bash
ffmpeg -i ch.mp3 -t 10 -ab 128k ch-trim.mp3 && mv ch-trim.mp3 ch.mp3
```

## Singapore event — minimum set

Drop in at least:
- `sg.mp3` — event location
- `ch.mp3` — Team A default (Switzerland)
- `de.mp3` — Team B default (Germany)
- Plus whatever nations the teams pick

5 × ~300 kB = under 2 MB total. Nothing crazy.
