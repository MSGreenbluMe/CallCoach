# CallCoach — AI Tréningový Bot pre Call Centrá

## Product Requirements Document (PRD)

**Verzia:** 1.0
**Dátum:** 2026-03-05
**Autor:** Miloš Svoboda / Konecta CZ
**Implementácia:** Claude Code + Streamlit

---

## 1. Vízia produktu

CallCoach je AI-powered tréningový simulátor pre operátorov call centier. ElevenLabs Conversational AI agent hrá rolu zákazníka, živý operátor trénuje svoje zručnosti v realistických scenároch. Po každom hovore Gemini LLM vyhodnotí kvalitu a poskytne spätnú väzbu.

**Prečo to robíme:** Klasické školenia (roleplay s kolegom, e-learning) sú neškálovateľné, nekonzistentné a nedajú sa objektívne merať. CallCoach umožňuje trénovať kedykoľvek, s konzistentným "zákazníkom", s okamžitým hodnotením a sledovaním progresu.

**Kľúčový princíp:** Každé cvičenie musí byť **kalibrovateľné** (nastaviteľná obtiažnosť), **reprodukovateľné** (rovnaký scenár = rovnaké podmienky) a **porovnateľné** (jednotné metriky naprieč agentmi a scenármi).

---

## 2. Používateľské role

### 2.1 Agent (Operátor/Trainee)
- Vyberá si scenáre a trénuje
- Vidí vlastné výsledky, progres, achievementy
- Počúva vlastné nahrávky
- Nemôže vytvárať scenáre

### 2.2 Manažér (Team Lead / Tréner)
- Vytvára a edituje scenáre
- Vidí dashboard celého tímu
- Priradí scenáre konkrétnym agentom
- Exportuje reporty
- Vidí detaily každého agenta

### 2.3 Admin
- Správa používateľov a tímov
- Systémové nastavenia (API kľúče, limity)
- Prístup ku všetkému

---

## 3. Technický stack

| Komponent | Technológia | Účel |
|-----------|-------------|------|
| Frontend + Backend | **Streamlit** | Web UI, session management, routing |
| Voice AI Agent | **ElevenLabs Conversational AI API** | Simulácia zákazníka (hlas) |
| Knowledge Base | **ElevenLabs Knowledge Base (RAG)** | Kontext scenára pre AI agenta |
| Evaluácia | **Gemini 3.1 Flash Lite API** | Hodnotenie kvality hovoru |
| Databáza | **SQLite** (MVP) → PostgreSQL (prod) | Persistencia dát |
| Audio storage | **Lokálny filesystem** (MVP) → S3 (prod) | Nahrávky hovorov |

### 3.1 Kľúčové API endpointy

**ElevenLabs Conversational AI:**
- Dokumentácia: https://elevenlabs.io/docs/eleven-agents/build/overview
- Knowledge Base: https://elevenlabs.io/docs/eleven-agents/customization/knowledge-base
- Agent sa vytvorí per scenár s: system prompt (customer persona), voice, knowledge base, language
- Conversation API: inicializácia hovoru, streaming audio, získanie transkriptu

**Gemini 3.1 Flash Lite:**
- Dokumentácia: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite-preview
- Vstup: transcript + scenario definition + evaluation criteria
- Výstup: štruktúrovaný JSON so skóre a feedbackom

---

## 4. Definícia scenára (Scenario Engine)

Scenár je základná jednotka tréningu. Každý scenár obsahuje:

### 4.1 Základné info
- `name` — názov scenára (napr. "Reklamácia poškodeného tovaru")
- `description` — krátky popis situácie
- `category` — kategória (enum: SALES, RETENTION, TECH_SUPPORT, COMPLAINTS, BILLING, ONBOARDING)
- `difficulty` — obtiažnosť 1-5 (1=ľahký zákazník, 5=veľmi náročný)
- `language` — jazyk hovoru (cs/sk/hu/en)
- `estimated_duration` — odhadovaný čas v minútach
- `max_duration` — maximálny čas hovoru (timeout)

### 4.2 Customer Persona
- `persona_name` — meno zákazníka (napr. "Jana Nováková")
- `persona_background` — backstory (napr. "45 rokov, učiteľka, nakúpila práčku pred 2 týždňami")
- `persona_mood` — nálada na začiatku hovoru (enum: CALM, FRUSTRATED, ANGRY, CONFUSED, IMPATIENT, FRIENDLY)
- `persona_patience` — level trpezlivosti 1-10 (koľko vydrží ak agent nepostupuje správne)
- `persona_communication_style` — popis štýlu komunikácie (napr. "Hovorí veľmi rýchlo, skáče do reči")
- `persona_hidden_need` — skrytá potreba, ktorú agent musí odhaliť (napr. "V skutočnosti chce vymeniť za lepší model, nie len reklamovať")

### 4.3 Cieľ hovoru (Call Objective)
- `primary_goal` — hlavný cieľ agenta (napr. "Vyriešiť reklamáciu a ponúknuť výmenu za vyšší model")
- `success_definition` — čo znamená úspech (napr. "Zákazník súhlasí s výmenou a je spokojný")
- `fail_conditions` — čo znamená neúspech (napr. "Zákazník žiada vedúceho / zákazník zavesí nahnevaný")

### 4.4 Povinné body (Mandatory Checkpoints)
Usporiadaný zoznam krokov, ktoré agent MUSÍ splniť. Každý checkpoint:
- `id` — identifikátor
- `name` — názov (napr. "Pozdrav a identifikácia")
- `description` — čo presne musí agent urobiť/povedať
- `order` — poradie (niektoré musia ísť v správnom poradí)
- `is_order_strict` — či je poradie striktné (true/false)
- `detection_hint` — hint pre LLM evaluátor čo hľadať v transkripcii

Príklad checkpointov pre reklamačný scenár:
1. Pozdrav a predstavenie sa
2. Overenie identity zákazníka (meno, číslo objednávky)
3. Aktívne vypočutie problému
4. Empatické vyjadrenie porozumenia
5. Zistenie detailov problému
6. Navrhnutie riešenia
7. Potvrdenie súhlasu zákazníka
8. Zhrnutie dohodnutých krokov
9. Profesionálne rozlúčenie

### 4.5 ElevenLabs Agent Config
- `elevenlabs_agent_id` — ID agenta v ElevenLabs (vytvorí sa cez API)
- `voice_id` — vybraný hlas
- `system_prompt` — celý prompt pre AI agenta (generuje sa z persona + scenára)
- `knowledge_base_docs` — dokumenty pre RAG (info o produktoch, cenníky, podmienky)
- `first_message` — prvá správa zákazníka (napr. "Dobrý deň, volám ohľadom objednávky...")
- `temperature` — kreativita agenta (nižšia = predvídateľnejší, vyššia = spontánnejší)

### 4.6 Evaluation Config
- `evaluation_weights` — váhy pre výpočet celkového skóre
- `bonus_criteria` — voliteľné bonusové body (napr. upsell, cross-sell)
- `penalty_criteria` — pokuty (napr. použitie zakázaných slov, prerušovanie)

---

## 5. Systém hodnotenia (Evaluation Engine)

### 5.1 Dvojvrstvové hodnotenie

#### Vrstva 1: Obecná kvalita hovoru (platí pre všetky scenáre)

| Kritérium | Popis | Rozsah |
|-----------|-------|--------|
| **Komunikačná jasnosť** | Zrozumiteľnosť, štrukturovanie myšlienok | 1-10 |
| **Empatia a rapport** | Prejavenie porozumenia, budovanie vzťahu | 1-10 |
| **Aktívne počúvanie** | Parafrázovanie, doplňujúce otázky | 1-10 |
| **Profesionálny jazyk** | Adekvátny slovník, žiadny slang, správne oslovenie | 1-10 |
| **Štruktúra hovoru** | Úvod → jadro → záver, logický postup | 1-10 |
| **Riadenie hovoru** | Schopnosť viesť hovor správnym smerom | 1-10 |
| **Zvládanie námietok** | Reakcia na odpor/nesúhlas zákazníka | 1-10 |

#### Vrstva 2: Scenárovo-špecifické hodnotenie

| Kritérium | Typ | Popis |
|-----------|-----|-------|
| **Splnenie checkpointov** | Binary per checkpoint | Každý povinný bod: splnený/nesplnený |
| **Poradie checkpointov** | Binary | Boli checkpointy splnené v správnom poradí? |
| **Dosiahnutie cieľa** | Enum: ACHIEVED / PARTIAL / FAILED | Bol hlavný cieľ hovoru dosiahnutý? |
| **Odhalenie skrytej potreby** | Binary | Agent odhalil hidden_need? |
| **Bonusové kritériá** | Podľa scenára | Upsell, cross-sell, NPS zmienka... |
| **Penalizácie** | Podľa scenára | Zakázané slová, prerušovanie, eskalácia |

### 5.2 Výpočet celkového skóre

```
overall_score = (
  general_quality_avg * weight_general +
  checkpoint_completion_pct * weight_checkpoints +
  goal_achievement_score * weight_goal +
  bonus_points - penalty_points
) / max_possible * 100
```

Defaultné váhy (konfigurovateľné per scenár):
- `weight_general` = 0.35
- `weight_checkpoints` = 0.35
- `weight_goal` = 0.30

### 5.3 Gemini Evaluation Prompt (šablóna)

LLM dostane štruktúrovaný prompt:
```
Analyzuj nasledujúci prepis hovoru medzi operátorom call centra a zákazníkom.

SCENÁR: {scenario.description}
CIEĽ AGENTA: {scenario.primary_goal}
POVINNÉ BODY: {scenario.checkpoints}

PREPIS HOVORU:
{transcript}

Vyhodnoť hovor podľa nasledujúcich kritérií a vráť JSON:
{evaluation_schema}

Pre každé kritérium uveď:
- score (číslo)
- evidence (konkrétna citácia z prepisu)
- recommendation (čo mohol agent urobiť lepšie)
```

Výstup: štruktúrovaný JSON (schéma definovaná, Gemini vráti JSON mode).

### 5.4 Kvalitatívna spätná väzba

Okrem čísiel Gemini generuje:
- **Summary** — 2-3 vety zhrnutie hovoru
- **Strengths** — čo agent urobil dobre (max 3 body)
- **Improvements** — čo by mohol zlepšiť (max 3 body)
- **Coaching tip** — jeden konkrétny tip na ďalší tréning

---

## 6. Gamifikácia

### 6.1 XP systém
- Dokončený hovor: **+50 XP** (base)
- Bonus za skóre: **+1 XP za každý bod nad 70%** (napr. skóre 85 = +15 XP bonus)
- Perfect score (100%): **+100 XP bonus**
- Prvé dokončenie scenára: **+25 XP**
- Daily streak bonus: **+20 XP**

### 6.2 Level systém

| Level | Názov | Požadované XP |
|-------|-------|---------------|
| 1 | Nováčik | 0 |
| 2 | Kadet | 200 |
| 3 | Junior Agent | 500 |
| 4 | Agent | 1000 |
| 5 | Senior Agent | 2000 |
| 6 | Expert | 4000 |
| 7 | Master | 7000 |
| 8 | Guru | 11000 |
| 9 | Legenda | 16000 |
| 10 | Call Center Jedi | 25000 |

### 6.3 Achievementy (Odznaky)

| Odznak | Podmienka | Ikona |
|--------|-----------|-------|
| Prvý hovor | Dokončiť prvý tréningový hovor | 🎯 |
| Perfekcionista | Získať 100% na ľubovoľnom scenári | ⭐ |
| Streak Master | 5 po sebe idúcich dní tréning | 🔥 |
| Empat roka | Priemer empatie > 9.0 (min 10 hovorov) | 💚 |
| Speed Demon | Dokončiť scenár pod 50% odhadovaného času s >80% | ⚡ |
| Polyglot | Dokončiť scenáre v 3 rôznych jazykoch | 🌍 |
| Kategória komplet | Dokončiť všetky scenáre v jednej kategórii | 🏆 |
| Záchranár | Zmeniť ANGRY zákazníka na spokojného (goal achieved) | 🛟 |
| Sales Shark | 5x úspešný upsell | 🦈 |
| Iron Man | 10 hovorov v jednom dni | 💪 |
| Comeback Kid | Po neúspešnom hovore hneď úspešný na tom istom scenári | 🔄 |
| Mentoring | (budúcnosť) Poskytnúť peer review kolegovi | 🤝 |

### 6.4 Leaderboard
- Filtre: týždenný / mesačný / celkový
- Metriky: XP, avg skóre, počet dokončených scenárov
- Tímový leaderboard (pre manažérov)

### 6.5 Milestones (Progress bars)
- "Dokončiť 10 hovorov" — progress bar s číslom
- "Dosiahnuť Level 5" — progress bar
- "Získať 5 achievementov" — progress bar
- Tieto sa zobrazujú na domovskej stránke agenta

---

## 7. User Flows

### Flow 1: Agent — Tréningová session

```
LOGIN
  ↓
AGENT HOME (dashboard s XP, levelom, achievementami)
  ↓
[Agent klikne "Začať tréning"]
  ↓
SCENARIO BROWSER (filtrovanie podľa kategórie, obtiažnosti, jazyka)
  ↓
[Agent vyberie scenár]
  ↓
PRE-CALL BRIEFING (kontext, cieľ, povinné body, info o zákazníkovi)
  ↓
[Agent klikne "Spustiť hovor"]
  ↓
ACTIVE CALL SCREEN (timer, waveform, objectives sidebar, "Ukončiť hovor")
  ↓
[Hovor prebieha cez ElevenLabs — real-time voice]
  ↓
[Agent alebo AI ukončí hovor]
  ↓
LOADING / EVALUATING (Gemini spracováva transcript)
  ↓
SCORECARD (celkové skóre, radar chart, checkpointy, feedback, coaching tip)
  ↓
[Agent vidí nové XP, prípadne nový achievement popup]
  ↓
[CTA: "Skúsiť znova" / "Ďalší scenár" / "Domov"]
```

### Flow 2: Manažér — Dashboard

```
LOGIN
  ↓
MANAGER DASHBOARD
  ├── Team Overview (karty: počet agentov, avg skóre, sessions tento týždeň)
  ├── Score Trends (line chart: tímový priemer v čase)
  ├── Top Performers (leaderboard)
  ├── Skill Gap Heatmap (kategórie vs kritériá)
  ↓
[Manažér klikne na agenta]
  ↓
AGENT DETAIL
  ├── Profil + level + XP
  ├── Score history (line chart)
  ├── Skills radar chart
  ├── Zoznam sessions (s možnosťou kliknúť na detail)
  ↓
[Manažér klikne na session]
  ↓
SESSION DETAIL
  ├── Celý scorecard
  ├── Audio playback
  ├── Plný transcript
  ├── Gemini evaluation detail
```

### Flow 3: Manažér — Správa scenárov

```
SCENARIO MANAGEMENT
  ├── Zoznam existujúcich scenárov (active/inactive toggle)
  ↓
[Manažér klikne "Vytvoriť nový"]
  ↓
SCENARIO EDITOR (multi-step form)
  Step 1: Základné info (názov, kategória, obtiažnosť, jazyk)
  Step 2: Customer Persona (meno, backstory, mood, patience, štýl)
  Step 3: Cieľ + povinné checkpointy (drag & drop poradie)
  Step 4: ElevenLabs config (výber hlasu, first message, knowledge base upload)
  Step 5: Evaluation config (váhy, bonus/penalty kritériá)
  Step 6: Preview & Test (manažér si sám vyskúša hovor)
  ↓
[Manažér klikne "Publikovať"]
  ↓
Scenár je dostupný pre agentov
```

---

## 8. Obrazovky (Wireframe popis)

### P1: Login
- Jednoduché prihlásenie: meno + team kód (MVP, bez auth providera)
- Dropdown na výber role (agent/manažér) — v produkcii cez permissions
- Logo CallCoach navrchu

### P2: Agent Home
- **Header:** Logo, meno agenta, level badge, XP bar do ďalšieho levelu
- **Stats row:** 3 karty — Celkový počet sessions | Priemerné skóre | Aktuálny streak (dní)
- **Recent achievements:** horizontálny scroll s poslednými odznakmi
- **Quick action:** Veľké tlačidlo "🎯 Začať tréning"
- **Recent sessions:** Tabuľka posledných 5 sessions (scenár, dátum, skóre, trvanie)
- **Milestones:** 2-3 progress bary pre aktívne milestones

### P3: Scenario Browser
- **Filtre:** Kategória (tabs) | Obtiažnosť (stars slider) | Jazyk (dropdown)
- **Scenario cards:** Grid layout, každá karta obsahuje:
  - Názov scenára
  - Kategória badge (farebný)
  - Obtiažnosť (hviezdičky)
  - Odhadovaný čas
  - Najlepšie dosiahnuté skóre (ak už bol scenár absolvovaný)
  - Stav: Nový / Absolvovaný / ✓ Zvládnutý (>80%)
- **Sorting:** Podľa obtiažnosti / názvu / odporúčané

### P4: Pre-Call Briefing
- **Hlavička:** Názov scenára + obtiažnosť + kategória
- **Sekcia "Kontext":** Popis situácie, čo sa deje
- **Sekcia "Váš zákazník":** Meno zákazníka, stručný popis (BEZ odhalenia mood/patience — to je na agentovi aby zistil)
- **Sekcia "Váš cieľ":** Čo musí agent dosiahnuť
- **Sekcia "Checkpoints":** Zoznam povinných bodov (viditeľný, agent vie čo sa od neho čaká)
- **Veľké tlačidlo:** "📞 Spustiť hovor"
- **Info:** "Hovor bude nahrávaný a vyhodnotený"

### P5: Active Call
- **Minimalistický dizajn** — agent sa musí sústrediť na hovor
- **Timer** navrchu (odpočítavanie ak je max_duration, inak nahor)
- **Názov scenára** + kategória badge
- **Audio waveform vizualizácia** — centrálny element
- **Collapsible sidebar:** "Pripomienka cieľov" — zoznam checkpointov (agent si môže pozrieť, ale nemalo by byť rušivé)
- **Veľké červené tlačidlo:** "Ukončiť hovor"
- **Status indicator:** "Hovor prebieha..." s animáciou

### P6: Evaluating (Loading)
- Animácia (spinner alebo progress)
- Text: "Vyhodnocujem váš hovor..."
- Krátke tipy počas čakania (rotujúce motivačné texty)

### P7: Scorecard
- **Veľké číslo** navrchu: celkové skóre (farebne: zelená >80, žltá 50-80, červená <50)
- **XP gained:** "+75 XP" animácia, prípadne level up
- **Achievement popup:** Ak bol získaný nový odznak
- **Radar chart:** 7 osí obecnej kvality
- **Checkpoint checklist:** Každý checkpoint s ✅ / ❌, s citáciou z transcriptu
- **Goal status:** ACHIEVED ✅ / PARTIAL ⚠️ / FAILED ❌
- **Feedback sekcia:**
  - Summary (2-3 vety)
  - ✅ Silné stránky (bullety)
  - 🔧 Na zlepšenie (bullety)
  - 💡 Coaching tip (zvýraznený box)
- **Audio playback:** Prehrať celý hovor
- **Transcript:** Expandable, plný prepis s farebným označením (agent vs zákazník)
- **CTA tlačidlá:** "Skúsiť znova" | "Ďalší scenár" | "Domov"

### P8: Manager Dashboard
- **Hlavička:** "Prehľad tímu" + dátumový filter
- **Stats karty:** Počet agentov | Priemer skóre (trend šípka) | Sessions tento týždeň | Aktívnych agentov dnes
- **Line chart:** Priemerné skóre tímu v čase (posledných 30 dní)
- **Leaderboard tabuľka:** Top 10 agentov (meno, level, avg skóre, sessions, trend)
- **Skill Gap Heatmap:** Riadky = kritériá kvality, stĺpce = agenti, farba = skóre
- **Scenario Completion:** Matrica scenárov vs agentov (kto čo absolvoval)

### P9: Agent Detail (Manager view)
- **Profil:** Meno, level, XP, achievementy
- **Score line chart:** Progres v čase
- **Radar chart:** Priemer cez všetky kritériá
- **Session log:** Sortovateľná tabuľka (dátum, scenár, skóre, trvanie) s kliknuteľnými detailmi
- **Recommendation:** LLM vygenerované odporúčanie na aký scenár by sa mal agent zamerať

### P10: Scenario Management
- **Tabuľka scenárov:** Názov, kategória, obtiažnosť, počet absolvovaní, avg skóre, active toggle
- **"Vytvoriť nový" button**
- **Kliknutie na scenár → Scenario Editor**

### P11: Scenario Editor
- **Multi-step formulár** (viď Flow 3)
- **Step navigation** navrchu (1-6 s progress bar)
- **Každý step je separátna sekcia** s formulárovými poliami
- **Step 4 (ElevenLabs):** Dropdown pre voice, textarea pre first message, file upload pre knowledge base
- **Step 6 (Preview):** "Vyskúšať hovor" button — manažér si zahrá agenta

### P12: Achievements Gallery
- **Grid odznakov** — všetky dostupné
- **Earned:** farebný, s dátumom získania
- **Locked:** šedý, s popisom podmienky
- **In progress:** farebný border, s progress bar
- **Filter:** Earned / Locked / All

---

## 9. Dátový model

### users
```
id              INTEGER PRIMARY KEY
name            TEXT NOT NULL
email           TEXT UNIQUE
role            TEXT CHECK(role IN ('agent','manager','admin'))
team            TEXT
avatar_url      TEXT
xp              INTEGER DEFAULT 0
level           INTEGER DEFAULT 1
streak_days     INTEGER DEFAULT 0
last_active     DATETIME
created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
```

### scenarios
```
id                      INTEGER PRIMARY KEY
name                    TEXT NOT NULL
description             TEXT
category                TEXT CHECK(category IN ('SALES','RETENTION','TECH_SUPPORT','COMPLAINTS','BILLING','ONBOARDING'))
difficulty              INTEGER CHECK(difficulty BETWEEN 1 AND 5)
language                TEXT DEFAULT 'cs'
estimated_duration_min  INTEGER
max_duration_min        INTEGER
persona_name            TEXT
persona_background      TEXT
persona_mood            TEXT
persona_patience        INTEGER
persona_comm_style      TEXT
persona_hidden_need     TEXT
primary_goal            TEXT
success_definition      TEXT
fail_conditions         TEXT
elevenlabs_agent_id     TEXT
voice_id                TEXT
system_prompt           TEXT
first_message           TEXT
knowledge_base_config   TEXT (JSON)
temperature             REAL DEFAULT 0.7
evaluation_weights      TEXT (JSON)
bonus_criteria          TEXT (JSON)
penalty_criteria        TEXT (JSON)
is_active               BOOLEAN DEFAULT 1
created_by              INTEGER REFERENCES users(id)
created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at              DATETIME
```

### checkpoints
```
id                  INTEGER PRIMARY KEY
scenario_id         INTEGER REFERENCES scenarios(id) ON DELETE CASCADE
name                TEXT NOT NULL
description         TEXT
order_index         INTEGER NOT NULL
is_order_strict     BOOLEAN DEFAULT 0
detection_hint      TEXT
```

### sessions
```
id                          INTEGER PRIMARY KEY
user_id                     INTEGER REFERENCES users(id)
scenario_id                 INTEGER REFERENCES scenarios(id)
started_at                  DATETIME
ended_at                    DATETIME
duration_seconds            INTEGER
audio_url                   TEXT
transcript                  TEXT
elevenlabs_conversation_id  TEXT
status                      TEXT CHECK(status IN ('in_progress','completed','abandoned','timeout'))
created_at                  DATETIME DEFAULT CURRENT_TIMESTAMP
```

### evaluations
```
id                      INTEGER PRIMARY KEY
session_id              INTEGER REFERENCES sessions(id) ON DELETE CASCADE
overall_score           REAL
communication_clarity   REAL
empathy_rapport         REAL
active_listening        REAL
professional_language   REAL
call_structure          REAL
call_control            REAL
objection_handling      REAL
checkpoint_results      TEXT (JSON: [{checkpoint_id, passed, evidence}])
checkpoint_order_ok     BOOLEAN
goal_achieved           TEXT CHECK(goal_achieved IN ('ACHIEVED','PARTIAL','FAILED'))
hidden_need_found       BOOLEAN
bonus_points            REAL DEFAULT 0
penalty_points          REAL DEFAULT 0
summary                 TEXT
strengths               TEXT (JSON array)
improvements            TEXT (JSON array)
coaching_tip            TEXT
raw_llm_response        TEXT
evaluated_at            DATETIME DEFAULT CURRENT_TIMESTAMP
```

### achievements
```
id                  INTEGER PRIMARY KEY
name                TEXT NOT NULL
description         TEXT
icon                TEXT
condition_type      TEXT NOT NULL
condition_value     TEXT NOT NULL
category            TEXT
```

### user_achievements
```
id              INTEGER PRIMARY KEY
user_id         INTEGER REFERENCES users(id)
achievement_id  INTEGER REFERENCES achievements(id)
earned_at       DATETIME DEFAULT CURRENT_TIMESTAMP
UNIQUE(user_id, achievement_id)
```

### xp_log
```
id          INTEGER PRIMARY KEY
user_id     INTEGER REFERENCES users(id)
session_id  INTEGER REFERENCES sessions(id)
xp_earned   INTEGER
reason      TEXT
created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
```

---

## 10. ElevenLabs integrácia — Detail

### 10.1 Agent Setup per scenár

Pri vytvorení scenára sa cez ElevenLabs API vytvorí agent:

```
POST /v1/convai/agents/create
{
  "name": "CallCoach - {scenario.name}",
  "conversation_config": {
    "agent": {
      "prompt": {
        "prompt": "{generated_system_prompt}",  // z persona + scenáru
        "llm": "gemini-2.0-flash-001",  // alebo Claude
        "temperature": {scenario.temperature}
      },
      "first_message": "{scenario.first_message}",
      "language": "{scenario.language}"
    },
    "tts": {
      "voice_id": "{scenario.voice_id}"
    }
  }
}
```

### 10.2 System prompt generovanie

Template pre customer persona prompt:
```
Si zákazník menom {persona_name}.

TVOJ PRÍBEH: {persona_background}

TVOJA NÁLADA: {persona_mood_description}
TVOJA TRPEZLIVOSŤ: {patience}/10

TVOJ KOMUNIKAČNÝ ŠTÝL: {persona_comm_style}

TVOJA SKRYTÁ POTREBA: {persona_hidden_need}

PRAVIDLÁ:
- Správaj sa ako skutočný zákazník, nie ako AI
- Reaguj emocionálne podľa svojej nálady
- Ak agent prejaví empatiu, tvoja nálada sa môže zlepšiť
- Ak agent ignoruje tvoje pocity alebo je neosobný, tvoja nálada sa zhorší
- Ak tvoja trpezlivosť klesne na 0, žiadaj vedúceho alebo zaves
- Nikdy neprezraď svoju skrytú potrebu priamo — agent ju musí odhaliť otázkami
- Odpovedaj v jazyku {language}
- Hovor prirodzene, s prípadnými "hm", pauzami, prerušeniami

KONTEXT HOVORU: {scenario.description}
```

### 10.3 Knowledge Base

Pre každý scenár sa do ElevenLabs RAG nahrajú relevantné dokumenty:
- Produktové informácie (čo zákazník kúpil)
- Cenníky
- Obchodné podmienky
- História zákazníka (predošlé objednávky)
- FAQ

Toto umožňuje AI zákazníkovi realisticky odpovedať na otázky agenta.

### 10.4 Konverzácia

```
1. Agent klikne "Spustiť hovor"
2. Frontend vytvorí WebSocket spojenie s ElevenLabs
3. Audio streaming obojsmerne
4. Po ukončení sa stiahne:
   - Transcript (cez conversation history API)
   - Audio nahrávka
   - Metadata (trvanie, počet turns)
```

---

## 11. Gemini evaluácia — Detail

### 11.1 Evaluation Pipeline

```
1. Session ukončená → transcript uložený
2. Zostavenie evaluation promptu:
   - System context (si evaluátor kvality)
   - Scenario definition (cieľ, checkpointy)
   - Full transcript
   - Evaluation schema (požadovaný JSON formát)
3. API call na Gemini 3.1 Flash Lite
4. Parse JSON response
5. Výpočet overall_score
6. Uloženie do evaluations tabuľky
7. Achievement check + XP calculation
8. Update user stats
9. Zobrazenie scorecardu
```

### 11.2 Gemini System Prompt

```
Si expert na kvalitu hovorov v call centre. Tvoja úloha je objektívne
vyhodnotiť nasledujúci hovor medzi operátorom a zákazníkom.

Buď prísny ale spravodlivý. Hodnoť na základe konkrétnych dôkazov
z prepisu, nie domnienok.

Vráť VÝHRADNE valídny JSON podľa nasledujúcej schémy, žiadny iný text:

{
  "communication_clarity": {"score": 1-10, "evidence": "...", "recommendation": "..."},
  "empathy_rapport": {"score": 1-10, "evidence": "...", "recommendation": "..."},
  "active_listening": {"score": 1-10, "evidence": "...", "recommendation": "..."},
  "professional_language": {"score": 1-10, "evidence": "...", "recommendation": "..."},
  "call_structure": {"score": 1-10, "evidence": "...", "recommendation": "..."},
  "call_control": {"score": 1-10, "evidence": "...", "recommendation": "..."},
  "objection_handling": {"score": 1-10, "evidence": "...", "recommendation": "..."},
  "checkpoints": [
    {"checkpoint_id": 1, "passed": true/false, "evidence": "..."}
  ],
  "checkpoint_order_correct": true/false,
  "goal_achieved": "ACHIEVED" | "PARTIAL" | "FAILED",
  "hidden_need_found": true/false,
  "summary": "2-3 vety zhrnutie",
  "strengths": ["...", "...", "..."],
  "improvements": ["...", "...", "..."],
  "coaching_tip": "..."
}
```

---

## 12. Ukážkové scenáre (pre MVP — 3 kusy)

### Scenár 1: Reklamácia — E-shop
- **Kategória:** COMPLAINTS
- **Obtiažnosť:** 2/5
- **Persona:** Jana Nováková, 45r, kúpila práčku pred 14 dňami, nefunguje odstreďovanie
- **Mood:** FRUSTRATED
- **Cieľ agenta:** Vyriešiť reklamáciu, ponúknuť výmenu za vyšší model
- **Hidden need:** Chce rýchle riešenie, nemá čas čakať na opravu
- **Checkpointy:** Pozdrav → ID overenie → Vypočutie → Empatia → Diagnostika → Riešenie → Súhlas → Zhrnutie → Rozlúčenie

### Scenár 2: Retencia — Telko
- **Kategória:** RETENTION
- **Obtiažnosť:** 4/5
- **Persona:** Martin Horák, 32r, programátor, chce zrušiť zmluvu (našiel lacnejší)
- **Mood:** CALM (ale rozhodnutý)
- **Cieľ agenta:** Udržať zákazníka, ponúknuť lepší tarif
- **Hidden need:** Nechce rušiť, len chce lepšiu cenu za rýchlejší internet
- **Checkpointy:** Pozdrav → ID → Dôvod odchodu → Empatia → Protiponuka → Handling námietok → Dohodnutie → Zhrnutie → Rozlúčenie

### Scenár 3: Tech Support — SW produkt
- **Kategória:** TECH_SUPPORT
- **Obtiažnosť:** 3/5
- **Persona:** Eva Malá, 58r, účtovníčka, nedokáže sa prihlásiť do aplikácie
- **Mood:** CONFUSED
- **Cieľ agenta:** Vyriešiť problém s prihlásením, naučiť zákazníčku reset hesla
- **Hidden need:** Má strach z technológií, potrebuje trpezlivé vysvetlenie krok za krokom
- **Checkpointy:** Pozdrav → ID → Popis problému → Upokojenie → Krokový návod → Overenie funkčnosti → Zhrnutie → Rozlúčenie

---

## 13. Bonusové nápady (post-MVP)

### 13.1 Sentiment Timeline
Vizualizácia emocionálneho oblúka hovoru — timeline kde vidíte ako sa nálada zákazníka menila od začiatku po koniec. Farebná čiara (červená → zelená). Identifikácia momentu zlomu (kedy sa sentiment otočil).

### 13.2 Coaching Mode
Voliteľný režim kde agent počas hovoru vidí real-time hinty ("Skús teraz prejaviť empatiu", "Zákazník znie nahnevane — spomaliť"). Tento režim sa nepočíta do skórovania. Ideálne pre úplných nováčikov.

### 13.3 Adaptive Difficulty
Zákazník (ElevenLabs agent) dynamicky mení svoju obtiažnosť na základe agentovho výkonu. Ak agent zvláda dobre → zákazník eskaluje. Ak sa agent trápi → zákazník trochu poľaví. Toto vytvára optimálnu zónu učenia.

### 13.4 A/B Call Comparison
Agent absolvuje rovnaký scenár 2x s rôznym prístupom. Systém porovná oba hovory vedľa seba — čo fungovalo lepšie.

### 13.5 Team Challenges
Manažér vytvorí týždennú výzvu (napr. "Kto dosiahne najvyššiu empatiu na scenári Reklamácia?"). Bonus XP pre top 3.

### 13.6 Call Replay s anotáciami
V transkripcii sa dajú označiť kľúčové momenty (pozitívne aj negatívne). Manažér alebo systém pridá anotácie. Agent sa z nich učí.

### 13.7 Benchmark Mode
Nahrá sa "ideálny hovor" (od experta alebo vygenerovaný). Nový agent porovná svoj hovor oproti benchmarku — kde sa líšil, čo vynechal.

### 13.8 Multi-language Dashboard
Dashboard aj evaluácia v CZ/SK/HU — pre celý cluster Konecta.

---

## 14. Štruktúra projektu (pre Claude Code)

```
callcoach/
├── app.py                      # Streamlit entry point + routing
├── requirements.txt            # Dependencies
├── config.py                   # API keys, constants, settings
├── database/
│   ├── db.py                   # SQLite connection + init
│   ├── models.py               # Data classes / ORM
│   └── seed.py                 # Seed data (demo scenarios, achievements)
├── services/
│   ├── elevenlabs_service.py   # ElevenLabs API wrapper
│   ├── gemini_service.py       # Gemini evaluation API wrapper
│   ├── evaluation_service.py   # Evaluation logic + scoring
│   ├── gamification_service.py # XP, levels, achievements logic
│   └── scenario_service.py     # Scenario CRUD + agent setup
├── pages/
│   ├── login.py                # P1: Login
│   ├── agent_home.py           # P2: Agent Home
│   ├── scenario_browser.py     # P3: Scenario Browser
│   ├── pre_call_briefing.py    # P4: Pre-Call Briefing
│   ├── active_call.py          # P5: Active Call
│   ├── scorecard.py            # P7: Scorecard + Results
│   ├── manager_dashboard.py    # P8: Manager Dashboard
│   ├── agent_detail.py         # P9: Agent Detail
│   ├── scenario_management.py  # P10+P11: Scenario CRUD + Editor
│   └── achievements.py         # P12: Achievements Gallery
├── components/
│   ├── radar_chart.py          # Radar chart component
│   ├── score_card.py           # Score display component
│   ├── achievement_badge.py    # Achievement badge component
│   ├── leaderboard.py          # Leaderboard component
│   └── audio_player.py         # Audio playback component
├── utils/
│   ├── prompt_templates.py     # LLM prompt templates
│   └── helpers.py              # Utility functions
└── data/
    ├── callcoach.db            # SQLite database
    └── audio/                  # Audio recordings
```

---

## 15. Konfigurácia a premenné prostredia

```env
# ElevenLabs
ELEVENLABS_API_KEY=
ELEVENLABS_DEFAULT_VOICE_ID=

# Gemini
GEMINI_API_KEY=

# App
APP_SECRET_KEY=
DATABASE_URL=sqlite:///data/callcoach.db
AUDIO_STORAGE_PATH=data/audio/
MAX_CALL_DURATION_MINUTES=15
DEFAULT_LANGUAGE=cs
```

---

## 16. MVP Scope (Fáza 1)

Čo MUSÍ byť v prvej verzii:
- ✅ Login (jednoduché, meno + team code)
- ✅ Agent Home s XP a levelom
- ✅ Scenario Browser (3 demo scenáre)
- ✅ Pre-Call Briefing
- ✅ Active Call cez ElevenLabs
- ✅ Transcript uloženie
- ✅ Gemini evaluácia
- ✅ Scorecard s radar chartom a feedbackom
- ✅ Základný Manager Dashboard (tím overview + agent detail)
- ✅ XP + Level systém
- ✅ 5 základných achievementov
- ✅ Leaderboard

Čo NIE je v MVP:
- ❌ Scenario Editor (scenáre sa seedujú cez kód)
- ❌ Coaching Mode
- ❌ Sentiment Timeline
- ❌ Adaptive Difficulty
- ❌ Peer Review
- ❌ Team Challenges
- ❌ Multi-language dashboard
- ❌ Audio playback (transcript stačí)
- ❌ Export reportov

---

*Dokument pripravený pre implementáciu v Claude Code.*
*Všetky API integrácie podľa oficiálnej dokumentácie ElevenLabs a Google Gemini.*
