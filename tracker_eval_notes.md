1. Odfiltruj z výstupu trackeru všechny objekty, které nejsou v ground truth.
    - Pak ti TrackEval bude hodnotit jen ty objekty, které jsou v anotaci.
    - Ale: to není standardní použití, a nepočítá s tím většina metrik jako FP/FN globálně správně.
    - NEJDE

2. Modifikuj samotný kód TrackEval, aby ignoroval některé třídy nebo detekce mimo zájmovou oblast.
    - To už je ale zásah do systému a vyžaduje úpravu zdrojového kódu.
    - NEJDE

3. Vytvoř si vlastní jednoduchou metodu na výpočet IDF1 jen pro anotované objekty.

    - Pokud sleduješ např. 3 brouky a máš jejich dráhy, můžeš vypočítat IDF1 mezi predikcí a GT jen na těchto entitách.
    
    - To je možná nejpřímější a nejčistší řešení v tvém kontextu.
    - THIS


Možnosti:
 - **IDF1**
    - $\text{IDF1} = \frac{2 \cdot \text{IDTP}}{2 \cdot \text{IDTP} + \text{IDFP} + \text{IDFN}}$

    - Např. máš jednoho brouka, sledovaného v 100 snímcích:
        - Tracker ho správně detekoval s dobrým ID ve 85 snímcích → IDTP = 85
        - Ve 10 snímcích měl špatné ID → IDFP = 10
        - Ve 5 snímcích tracker brouka vůbec neviděl → IDFN = 5
        - $\text{IDF1} = \frac{2 \cdot 85}{2 \cdot 85 + 10 + 5} = \frac{170}{170 + 10 + 5} = \frac{170}{185} \approx 0.9189$

 - **Identity switches** = kolikrát ID změnil (IDFP)
 - **Track Lost Frames** = kolik snímků neměl žádné track ID přiřazené (track lost) (IDFN)

 - **Per-object (partial) tracking analysis:**
    - Hodnotíš tracker jen pro několik vybraných objektů.
    - Vypočítáš pro každý z nich:
        - Track consistency – zda má objekt stejné ID po celou dobu.
        - Track completeness – kolik snímků objekt byl správně sledován.
        - ID switches – počet změn ID.
        - Fragmentace – kolikrát se sledování přerušilo.
    - Vhodné pro výzkum a ladění trackeru na těžkých datech.
    - Není to globální metrika, ale může být dost užitečná.

- Surrogate metrics bez GT (heuristiky)
- Např.:
    - Average track length – pokud jsou tracky často krátké, značí to časté ztráty.
    - Track fragmentation count – kolikrát track skončí a znovu začne - FRAGMENTATION
    - Number of unique track IDs – pokud tracker vytváří hodně ID, může to indikovat over-splittin

