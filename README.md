# 🛡️ PTAC Sentinel

**PTAC Sentinel** ir inovatīva, preventīva drošības sistēma patērētāju tiesību aizsardzībai digitālajā vidē. Sistēmas pamatmērķis ir proaktīvi identificēt bīstamu preču trendus sociālajos tīklos (TikTok), atrast to izplatības vietas Latvijas e-komercijas telpā un veikt automātisku AI drošības auditu.

## 🔄 Darbības plūsma (Soli pa solim)

1. **Jomas ievade un Trendu ģenerēšana:** Lietotājs (inspektors) ievada kategoriju. Izmantojot AI (Google Gemini), sistēma uzģenerē aktuālos aktuālos produktus un atslēgvārdus.
2. **Globālā skenēšana (TikTok):** Izmantojot `Apify` TikTok API, sistēma reāllaikā iegūst datus par izvēlēto atslēgvārdu vai hashtag popularitāti un izveido hashtag mākoni (Hashtag Cloud).
3. **Viedā lokālā tirgus skenēšana (Tavily):** Sistēma meklē Latvijas digitālajā telpā e-komercijas veikalus, kas pārdod doto produktu. Tiek automātiski izslēgti salīdzinājumu portāli (salidzini.lv utt.), sociālie tīkli un ziņu lapas.
4. **AI Digitālais audits (Gemini 2.0 Flash):** Katram atrastajam e-veikalam tiek veikts padziļināts AI audits, lai pārbaudītu:
   - Vai ir redzams CE marķējums?
   - Vai ir norādīta ražotāja informācija?
   - Vai drošības pamācības un informācija ir latviešu valodā?
   - Vai pastāv vecuma ierobežojumi?
5. **Riska aprēķins:** Tiklīdz dati ir iegūti, tiek aprēķināts riska rādītājs (0-100). Virs 70 punktiem rezultāts tiek norādīts kā kritisks un nodots inspektoram padziļinātai pētniecībai.

## ⚙️ Tehnoloģiskais steks (2026. gads)

Sistēma nesen piedzīvoja pilnu pāreju no agrīna Streamlit prototipa uz modernu, dalītu, uz servisiem balstītu arhitektūru.

- **Backend (API):** Python 3.10+, FastAPI (`api.py`), Pydantic modelēšanai, Asynchronous IO (`asyncio`).
- **Frontend (UI):** React 19 + Vite (`frontend/` mape).
- **Mākslīgais intelekts:** Google Gemini (`gemini-2.0-flash`).
- **Datu ieguve:** Apify (TikTok), Tavily (E-komercija).
- **Testēšana:** `pytest` ar asinhroniem unit testiem (`tests/`).
- **Ieviešana (Deployment):** Docker un Docker Compose infrastruktūra.

## 🚀 Kā palaist projektu

Piezīme: repozitorijā nav atsevišķas `api/` mapes. Backend entrypoint ir fails `api.py`, savukārt HTTP endpointi ir pieejami zem URL prefiksa `/api/...`.

Visērtākais veids ir izmantot pievienoto `docker-compose.yml` konfigurāciju:

```bash
docker-compose up --build
```
- Frontend būs pieejams `http://localhost` (vai attiecīgajā portā, kas norādīts 80).
- Backend API atradīsies uz `http://localhost:8000`.

### Lokāla palaišana izstrādei (Development mode)

1. **Backend:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate # (vai .venv\Scripts\activate uz Windows)
   pip install -r requirements.txt
   uvicorn api:app --reload --port 8000
   ```
2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 📂 Projekta struktūra

- `api.py` – FastAPI aplikācijas pamats un maršrutēšana. Tas nav direktorijs `api/`, bet viens backend entrypoint fails.
- `main.py` – Orķestratora `PTACSentinel` klase.
- `src/` – Biznesa loģika un API servisi:
  - `config.py` – `.env` vides mainīgo un konfigurāciju pārvaldība (Pydantic Settings).
  - `models.py` – Sistēmas datu struktūras.
  - `services/` – Apify, Tavily, un Gemini integrācijas implementācijas.
- `frontend/` – React lietotnes avota kodi.
- `tests/` – Automatizētie koda testi.

---
## 🔑 API Atslēgas un vides mainīgie

Visas atslēgas ir jāiestata `.env` failā projekta saknē. Ērtākais veids ir nokopēt `.env.example` uz `.env` un aizpildīt vērtības:

```bash
cp .env.example .env
```

* `APIFY_API_KEY` (Obligāts) - TikTok datu iegūšanai.
* `TAVILY_API_KEY` (Obligāts) - Primārais rīks Latvijas e-komercijas veikalu meklēšanai.
* `GEMINI_API_KEY` (Obligāts) - E-veikalu satura drošības auditam (Google Gemini).
* `OPENAI_API_KEY` (Obligāts) - Komerciālo kategoriju populārāko trendu ieteikšanai un analīzei sākuma fāzē.
* `SERP_API_KEY` (Neobligāts) - Serper API atslēga, kas sistēmas konfigurācijā saglabāta kā alternatīva Tavily API lokālā tirgus skenēšanai (rezervei vai nākotnes vajadzībām).
