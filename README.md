# Sable — Traduzione italiana (mod non ufficiale)

Localizzazione italiana **non ufficiale** per [Sable](https://store.steampowered.com/app/757310/Sable/) (Shedworks / Raw Fury, 2021).

Il gioco non offre una traduzione italiana ufficiale. Questa mod inietta una localizzazione completa al runtime tramite [BepInEx](https://github.com/BepInEx/BepInEx) + [Il2CppInterop](https://github.com/BepInEx/Il2CppInterop), senza modificare i file originali del gioco.

## Stato della traduzione

| Sezione | Stato |
|---|---|
| Menù principale e UI (titolo, impostazioni, mappa, inventario, foto, scambi…) | ✅ 315/315 |
| Nomi e descrizioni oggetti | ✅ 250/250 |
| Descrizioni negozio | ✅ 17/17 |
| Dialoghi narrativi (Ink) | ✅ 4789/5109 (94%) |
| Nomi luoghi sulla mappa | ⚠️ in inglese (originali) |

Il rimanente 6% degli script Ink è fatto di identificatori interni del motore narrativo che **non vanno tradotti** (rompono il gioco).

## Installazione (utente finale)

> Versione testata: Sable su Heroic Games Launcher (Linux + Wine). Su Windows / Steam dovrebbe funzionare con gli stessi passaggi, sostituendo i percorsi.

### 1. Scarica il pacchetto della mod

Vai nella sezione [Releases](../../releases) e scarica l'ultimo `SableItalianMod-vX.Y.Z.zip`.

### 2. Installa BepInEx 6 IL2CPP nel gioco

1. Scarica `BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.NNN.zip` da [https://builds.bepinex.dev/projects/bepinex_be](https://builds.bepinex.dev/projects/bepinex_be) (build "BE", **non** la stable).
2. Estrai l'archivio nella cartella di Sable, ovvero la cartella che contiene `Sable.exe`.
   - **Heroic + Wine:** tipicamente `~/Games/Heroic/Sable/`
   - **Steam:** `<libreria Steam>/steamapps/common/Sable/`
3. Avvia il gioco una volta e poi chiudilo: BepInEx genera la struttura `BepInEx/plugins/`, `BepInEx/interop/`, `BepInEx/config/`.

### 3. Imposta il DLL override (solo Wine/Proton)

Su Wine devi forzare l'override di `winhttp.dll` aggiungendo la variabile d'ambiente al lancio del gioco.

**Heroic Games Launcher:**

1. Tasto destro su Sable → *Settings* → *Advanced* → *Environment Variables*.
2. Aggiungi:
   - **Name:** `WINEDLLOVERRIDES`
   - **Value:** `winhttp=n,b`

**Steam Proton:** in Properties → Launch Options:
```
WINEDLLOVERRIDES="winhttp=n,b" %command%
```

### 4. Installa la mod

Estrai il contenuto di `SableItalianMod-vX.Y.Z.zip` dentro:
```
<cartella di Sable>/BepInEx/plugins/SableItalianMod/
```

La struttura finale deve essere:
```
Sable/
├── Sable.exe
├── winhttp.dll
├── BepInEx/
│   ├── plugins/
│   │   └── SableItalianMod/
│   │       ├── SableItalianMod.dll
│   │       ├── it_strings.csv
│   │       ├── it_items.csv
│   │       └── sable_it.bin
│   └── …
└── …
```

### 5. Avvia il gioco

La lingua selezionata nel menù di Sable può rimanere su **English** — la mod intercetta i testi in inglese e li sostituisce con la versione italiana. Se vedi ancora del testo in inglese, controlla `BepInEx/LogOutput.log` per i messaggi di errore del plugin.

## Compilare la mod da sorgente

Richiede **.NET SDK 6.0+** e una copia di Sable installata.

```bash
git clone https://github.com/Sam4000133/sable-italian.git
cd sable-italian/SableItalianMod
dotnet build -c Release
```

Il `.csproj` cerca le DLL di BepInEx in `tools/BepInEx-IL2CPP/BepInEx/core/`. Scaricale come indicato al punto 2 sopra prima di compilare.

L'output (`bin/Release/net6.0/SableItalianMod.dll`) va copiato in `BepInEx/plugins/SableItalianMod/` insieme ai CSV e al `.bin` da `translations/`.

## Architettura della mod

La traduzione viene applicata via **Harmony patches** su quattro punti del gioco:

1. **`TextProvider_EN` getters** — sovrascrive le proprietà che restituiscono le stringhe UI in inglese.
2. **`LocalisedText.UpdateText`** — postfix che intercetta il dispatcher universale di testo UI (necessario per la TitleScreen che bypassa i getter diretti).
3. **`ItemDefinition.GetName/GetDescription/GetShopDescription`** — postfix che traduce i nomi e le descrizioni degli oggetti dell'inventario e del negozio.
4. **`UnityEngine.TextAsset.get_text`** — postfix che, quando l'asset richiesto è `sable.bin` (script Ink narrativi), restituisce la nostra versione tradotta.

## Contribuire alle traduzioni

I file sorgente di traduzione sono in `translations/`:

- `it_strings.csv` — UI: 3 colonne `property,en,it`
- `it_items.csv` — oggetti: 4 colonne `Name,Name_IT,Description_IT,ShopDescription_IT`
- `ink_strings.csv` — dialoghi: 3 colonne `path,en,it`

Per correggere una traduzione apri una pull request modificando direttamente la colonna `it`. Dopo aver modificato `ink_strings.csv` rigenera il binario:

```bash
python3 -m venv venv && source venv/bin/activate
pip install UnityPy
python3 scripts/inject_ink.py
```

Il file `translations/sable_it.bin` aggiornato verrà letto al prossimo avvio del gioco.

### Convenzioni di traduzione

Termini di lore mantenuti in inglese: *Cuts, Glider, Hoverbike, Chum, Ibexii, Hicaris, Whale, Sandwyrm*.

Toponimi non tradotti: *The Wash, Hakoa, Eccria, Sansee, Redsee, Sodic Waste, Midden, Burnt Oak Station, Badlands, Crystal Plateau*.

Personaggi (nomi propri) non tradotti: *Sizo, Sandip, Iria, Hamza, Garay, Jadi, Driss, Hilal, Saima, Zayna, Maz, Tej, Yoshi, Casii, Tohta, Llhor*.

Ruoli e gilde tradotti: *Cartographers → Cartografi, Machinists → Macchinisti, Scrappers → Rottamatori, Anglers → Pescatori, Climbers → Scalatori, Mask Caster → Forgiatore di Maschere*.

Termini di gameplay tradotti: *Compass → Bussola, Navigator → Navigatore, Stamina → Vigore*.

## Disclaimer

Questa è una mod fan-made, non affiliata né approvata da **Shedworks** o **Raw Fury**. Sable è © Shedworks / Raw Fury. Devi possedere una copia legale del gioco per usare la mod. Non viene ridistribuito alcun file del gioco originale.

## Licenza

Codice e traduzioni: [MIT](LICENSE).
