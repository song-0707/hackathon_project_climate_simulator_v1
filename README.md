# 🌍 Student Climate Simulator (AI Powered)

Welcome to the **Student Climate Simulator**, an interactive, educational web application designed to teach students about the complex trade-offs involved in global climate policy. 

## DEMO video: https://youtu.be/lFew4lFTfeI
---

Built using Streamlit, this simulator places the user in the role of a global leader. You must make hard decisions across different sectors (Forestry, Transportation, Energy) while balancing four critical metrics:
*   🌡️ **Global Temperature**
*   ☁️ **Carbon Emissions**
*   💰 **National Budget**
*   😊 **Public Support**

---

## 🚀 Features & Core Mechanics

### 🧠 Predictive AI Engine
Unlike standard games with hard-coded outcomes, this simulator is powered by a **Machine Learning Model** (a Random Forest Regressor). 
*   **Counterfactual Predictions:** Before you make a decision, the UI runs your potential choice through the AI model and displays the *exact predicted numerical impact* (e.g., `Temp: +0.15°C | Support: -85.0%`) directly on the policy cards.
*   **Dynamic Outcomes:** The AI model processes 11 different underlying environmental features (like deforestation rates, fossil fuel use, and urbanization) to calculate realistic changes to the global climate and economy.

### 📚 Educational Framework
The application is structured to maximize learning:
*   **UN Sustainable Development Goals (SDGs):** Every stage and policy choice is explicitly linked to real-world UN SDGs (e.g., 🌱 SDG 15: Life on Land, ⚡ SDG 7: Affordable and Clean Energy).
*   **"Learn the Science" Hub:** A dedicated reading pane explains the real-world science behind *why* you are making these choices (e.g., explaining what "Carbon Sinks" are).
*   **Interactive Tooltips:** Every core metric features hoverable tooltips explaining the scientific measurements (like Megatons of CO2) and their critical failure thresholds.

### ⚖️ High-Stakes Gameplay
Choices matter. You must achieve the specific stage goals (like lowering emissions) without bankrupting the country or angering the citizens.
*   **Immediate Failure States:** The simulator track metrics in real-time. If Global Temperature hits 2.0°C, Public Support drops below 20%, or the Budget hits $0, the game triggers an immediate **Game Over** with an explicit lesson on why that threshold is catastrophic.
*   **Trap Policies:** Be careful! Tempting policies (like "Abolish Public Transit" or "Sell Forests") act as traps that provide massive short-term gains but guarantee catastrophic failure.

### 🖥️ Unified PC-Friendly Layout
The UI is designed as a professional, compact 3-column dashboard that fits cleanly on a standard 1080p screen without excessive scrolling. 
*   **Left Column:** Educational Curriculum & Stage Goals.
*   **Center Column:** Live Data Trends & AI Scientific Feedback.
*   **Right Column:** Action Center & Predictive Policy Cards.

---

## 🎮 Gameplay Loop & Rules

As the newly elected global leader, your term is divided into **3 Stages**. Each stage presents a new environmental sector you must manage. Within each stage, there are **2 Rounds** where you must select a policy.

### 📜 The Rules of Survival
1. **The Primary Goal:** Complete all 3 Stages without allowing any of the 4 Core Metrics to breach their critical failure thresholds.
2. **Win Condition:** If you survive all 3 stages, the game evaluates your final Global Temperature against a target benchmark (e.g., keeping it strictly below 1.5°C) to determine if you achieved a "True Victory" or merely survived.
3. **Instant Game Over Triggers:** If at *any* point your metrics hit these limits, you are immediately removed from office and the game ends:
    *   🌡️ **Temperature:** Hits or exceeds **2.0°C** (Irreversible Ecological Collapse).
    *   ☁️ **Carbon Emissions:** Hits or exceeds **350.0 Mt** (Runaway Greenhouse Effect).
    *   💰 **Budget:** Drops to or below **$0** (National Bankruptcy).
    *   😡 **Public Support:** Drops to or below **20%** (Citizen Uprising/Riot).

---

## 🏛️ The Policy Breakdown & Trade-Offs

The core of the simulator lies in its balanced policy choices, each linked to a UN Sustainable Development Goal (SDG). There are no "perfect" answers; every choice requires a sacrifice.

### Stage 1: The Forestry Crisis
**Goal:** Lower Carbon Emissions to 160.0 Mt or lower AND keep Public Support above 50%.
*   **Round 1 Options:**
    *   `Option A [SDG 15]:` **Total Ban on Logging**. Plummets deforestation, but the sheer cost of enforcing it hurts the National Budget.
    *   `Option B [SDG 2]:` **Empower Local Communities**. A slower, balanced approach that slightly lowers deforestation while increasing Public Support.
    *   *💥 Trap Policy [SDG 15]:* **Sell Forests to Logging Conglomerate**. Instantly grants massive Budget wealth (+$200M), but spikes carbon and plummets Support by 85%, triggering an instant riot (Game Over).
*   **Round 2 Options:**
    *   `Option A [SDG 2]:` **Tax Meat Products**. Rapidly drops methane (carbon) emissions and earns Budget money, but citizens hate expensive food (-15% Support).
    *   `Option B [SDG 9]:` **Fund Fake-Meat Research**. Hugely popular with citizens (+15% Support) and lowers methane, but drains the Budget through massive grants.

### Stage 2: The Urban Infrastructure Challenge
**Goal:** Maintain the Budget above $300M while keeping Global Temperature below 1.5°C.
*   **Round 1 Options:**
    *   `Option A [SDG 11]:` **Buy Thousands of Electric Buses**. Lowers traffic and carbon, but makes cities crowded and costs a significant amount of Budget.
    *   `Option B [SDG 9]:` **Build a Mega High-Speed Railway**. Massive drop in fossil fuel use and huge Public Support, but drains an astronomical $120M from the Budget.
    *   *💥 Trap Policy [SDG 11]:* **Abolish Public Transit & Build 10-Lane Highways**. Eliminating transit costs saves the government billions, but causes massive carbon spikes (+45 Mt) and immediate temperature increases that can end the game.
*   **Round 2 Options:**
    *   `Option A [SDG 11]:` **Force Mandatory Carpooling**. Costs absolutely $0 and drastically cuts emissions, but the loss of freedom crashes Public Support (-15%).
    *   `Option B [SDG 13]:` **Subsidize Electric Cars for Everyone**. Everyone loves free EVs (+10% Support) and smog vanishes, but it costs a huge chunk of the Budget.

### Stage 3: The Energy & Industry Transition
**Goal:** The Final Push. Bring Temperature down to 1.1°C or lower.
*   **Round 1 Options:**
    *   `Option A [SDG 7]:` **Build the World's Largest Solar Farm**. A safe, massive reduction in fossil fuels and carbon, but installing it is incredibly expensive (-$100M).
    *   `Option B [SDG 7]:` **Build a Nuclear Power Plant**. Produces unparalleled zero-carbon energy, but citizens are terrified of meltdowns, crashing Support (-25%).
    *   *💥 Trap Policy [SDG 13]:* **Subsidize Unregulated Coal Mining**. The absolute cheapest option that gives everyone cheap power. Boosts Support and Budget, but guarantees catastrophic global warming (+0.30°C) which leads to a Game Over.
*   **Round 2 Options:**
    *   `Option A [SDG 13]:` **Charge Polluters a Carbon Tax**. The fastest way to make the government rich (+$150M) and stop pollution, but furious corporations pass the costs to citizens, destroying Support (-30%).
    *   `Option B [SDG 9]:` **Fund Experimental Carbon Vacuums**. Futuristic Direct Air Capture science that sucks carbon directly from the sky. Incredibly effective (-80 Mt Carbon) and somewhat popular, but drains nearly all remaining Budget.

---

## 🌍 Multi-Language Support (i18n)

The simulator supports **11 languages** powered by the Google Translate API via the `deep-translator` library. Switch instantly using the **Language** dropdown in the  sidebar.

| Flag | Language | Code |
|------|----------|----- |
| 🇬🇧 | English *(default)* | `en` |
| 🇮🇩 | Bahasa Indonesia | `id` |
| 🇲🇾 | Bahasa Melayu | `ms` |
| 🇨🇳 | 中文 (简体) | `zh-CN` |
| 🇯🇵 | 日本語 | `ja` |
| 🇰🇷 | 한국어 | `ko` |
| 🇸🇦 | العربية | `ar` |
| 🇫🇷 | Français | `fr` |
| 🇪🇸 | Español | `es` |
| 🇩🇪 | Deutsch | `de` |
| 🇮🇳 | हिन्दी | `hi` |

### ⚡ Caching — How it Works

Translations are cached permanently in `.translation_cache.json` so each language is only ever translated **once** via API, then loaded instantly from disk on all future uses.

**First-time use:** Switching to a new language triggers one API translation (~30-90 seconds). The app will warn you in advance with an estimated time.

**Pre-cache all languages at once** (recommended for offline or slow-connection deployments):
```bash
python preload_translations.py
```

This runs once and translates all 11 languages into the cache. After it completes, all language switches are less than 1 second.

---

## 🛠️ Technology Stack
This project is built purely in Python and leverages the following libraries:
*   **[Streamlit](https://streamlit.io/):** The core front-end framework used to render the interactive web dashboard.
*   **[Pandas](https://pandas.pydata.org/):** Used for managing the underlying state features and historical game data.
*   **[Scikit-Learn](https://scikit-learn.org/):** (via `joblib`) Used to load and execute the `climate_model.pkl` Random Forest Regressor for AI predictions.
*   **[Plotly](https://plotly.com/python/):** Used to render historical Temperature and Budget line charts.
*   **[deep-translator](https://pypi.org/project/deep-translator/):** Free, no-API-key library that calls Google Translate to power the multi-language support.

---

## 💻 How to Run & Preview

### 🌐 Live Online Preview
You can play the Student Climate Simulator directly in your browser without downloading any code!
**Play Now:** 👉 [Live Streamlit App](https://hackathonprojectclimatesimulatorv1-chqrnnhkjfeoikvmec6rz9.streamlit.app/)

### 🛠️ Local Installation
If you want to run the code locally or modify the AI model:
1. Clone the repository to your local machine.
2. Ensure you have Python 3.8+ installed.
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```
4. *(Optional but recommended)* Pre-cache all 11 languages so switching is instant:
```bash
python preload_translations.py
```

### Execution
Run the following command in your terminal from the project root directory:
```bash
streamlit run hackathon.py
```
The application will automatically open in your default web browser at `http://localhost:8502`.

> **💡 Note on first-time translation:** If you skip the preload step, switching to a non-English language for the first time will take 30–90 seconds while the app calls the Google Translate API. After that first load, the translation is permanently cached and loads in under 1 second.

---
*Built for educational purposes to simulate the complex realities of climate change policy.*
