# KNN - Beetle tracking

#### Authors:
- Dalibor Kříčka (xkrick01)
- Jakub Pekárek (xpekar19)
- Pavel Osinek (xosine00)
#### 2025, Brno
 
---

## Data k projektu

Veškerá data relevatní k tomuto projektu je možné nalézt na [Google Drive](https://drive.google.com/drive/folders/10Eu2y_Ief9yyekn0N4Fv8GMXV4uJlnSl?usp=sharing).

Odkazovaný adresář obsahuje konkrétně následující položky:
 - `beetle_detection_model/` - dotrénovaný detekční model pro detekci brouků
 - `dataset_annotated_detection/` - datová sada s anotacemi brouků pro dotrénování modelu
 - `dataset_ground_truth_tracks/` - datová sada anotovaných (ground truth) tras jednotlivých brouků pro vyhodnocení trackingu
 - `original_videos/` - původní dostupná data/videa, ze kterých projekt vychází
 - `splitted_videos/` - úryvky původních videí po 150 snímcích pro účely vytváření anotací jednotlivých tras
 - `tracking_results/` - výsledky trasování zmiňovaných tracking algoritmů pro jednotlivá původních videa (pro celé záznamy) - použito pro vyhodnocení přesnosti trasování
 - `tracking_eval_results/` - výsledky vyhodnocení výsledků z `tracking_results/` na všech ground truth z `dataset_ground_truth_tracks/`
 - `video_examples_tracking/` - videoukázka sledování a trasování brouků

## Zdrojové soubory k projektu

Zdrojové soubory skriptů využité při práci na projektu:

* `src/`
    * `annotators/` - Nástroje k anotaci brouků/tras pro detekci/tracking
        * annotator_detection_win.py
        * annotator_detection.py
        * annotator_gt_tracking_win.py
        * annotator_gt_tracking.py

    * `convertors/` - Převodníky mezi formáty dat, se kterými některé nástroje pracují
        * convert_boxmot_to_json.py
        * convert_json_to_yolo.py

    * `detection/` - Nástroje k dotrénování, validaci a testovací výstup detekčního modelu
        * predict.py
        * train.py
        * validation.py

    * `tracking/` - Nástroje a konfigurace pro tracking a jeho vyhodnocení
        * **beetle_tracker.py - produkuje strojově zpracovatelný výstup tras brouků pro zvolený video záznam**
        * botsort_beetle.yaml
        * bytetrack_beetle.yaml
        * evaluate_tracking.py
        * proccess_tracking_results.py

    * `video_processing/` - Pomocné nástroje pro zpracování videí
        * crop_video_images.py
        * video_splitter.py


## Popis jednotlivých zdrojových souborů
### Nástroje pro anotování
### `annotator_detection.py` a `annotator_detection_win.py`:

Nástroj načte snímky s brouky z adresáře, které je třeba anotovat, a spustí GUI ve kterém je možné pomocí klávesnice a myši všechny objekty označit příslušnými _bounding boxy_. Následně ukládá data v _JSON_ formátu, který obsahuje souřadnice vytvořených bounding boxů pro jednotlivé snímky.

Ovládání:
```
Klávesy:
  A - předchozí snímek v adresáři
  D - následující snímek v adresáři
  E - přepnutí do označovacího režimu / potvrzení vytvořeného bounding boxu
  Q - smazání označeného bounding boxu / přepnutí z označovacího režimu bez potvrzení bounding boxu
  R - zapnutí / vypnutí viditelnosti již vytvořených bouding boxů
  S - uložení všech vytvořených bounding boxů do JSON souboru
  X - vypnutí aplikace (POZOR! - bez uložení)

Myš:
  kolečko - přiblížení
  kliknutí a posunutí - orientace po připleženém snímku
```

Spuštění:
```
annotator_gt_tracking.py [-h] -f FOLDER [-i INPUT] -o OUTPUT

options:
  -h, --help           vypíše nápovědu k programu
  -f, --folder FOLDER  cesta k adresáři se snímky
  -i, --input INPUT    cesta k případnému vstupnímu JSON souboru s anotacemi
  -o, --output OUTPUT  cesta k výstupnímu JSON souboru pro uložení anotací
```

Verze programu:
 - pro Linux: `annotator_detection.py`
 - pro Windows: `annotator_detection_win.py`

Výstup tohoto programu je možné pomocí převodníku `convert_json_to_yolo.py` převést do formátu anotací pro trénování YOLO detekčního modelu.



### `annotator_gt_tracking.py` a `annotator_gt_tracking_win.py`:

Nástroj načte video a spustí GUI ve kterém je možné pomocí klávesnice a myši označit příslušnými _bounding boxy_ brouků. Konkrétně na každém snímku jednoho, čímž je vytvořena ground truth jedné trasy pro určitého brouka. Následně ukládá data v _JSON_ formátu, který obsahuje souřadince vytvořených bounding boxů pro jednotlivé snímky videa.

Je doporučené na vstup volit videa s maximálně 400 snímky pro zachování plynulosti programu. Pro rozdělení původních videí do kratších segmentů je možné využít nástroj `video_splitter.py`. Případně jsou dostupné již rozdělené záznamy po 150 snímcích v adresáři `splitted_videos/` na [Google Drive](https://drive.google.com/drive/folders/10Eu2y_Ief9yyekn0N4Fv8GMXV4uJlnSl?usp=sharing).

Ovládání:
```
Klávesy:
  A - předchozí snímek v adresáři
  D - následující snímek v adresáři
  E - přepnutí do označovacího režimu / potvrzení vytvořeného bounding boxu
  Q - smazání označeného bounding boxu / přepnutí z označovacího režimu bez potvrzení bounding boxu
  R - zapnutí / vypnutí viditelnosti již vytvořených bouding boxů
  S - uložení všech vytvořených bounding boxů do JSON souboru
  X - vypnutí aplikace (POZOR! - bez uložení)

Myš:
  kolečko - přiblížení
  kliknutí a posunutí - orientace po připleženém snímku
```

Spuštění:
```
annotator_gt_tracking.py [-h] -v VIDEO [-o OUTPUT] [-i INPUT] [-int START END]

options:
  -h, --help                    vypíše nápovědu k programu
  -v, --video VIDEO             cesta k videu
  -o, --output OUTPUT           cesta k výstupnímu JSON souboru pro uložení anotací
  -i, --input INPUT             cesta k případnému vstupnímu JSON souboru s anotacemi
```

Verze programu:
 - pro Linux: `annotator_gt_tracking.py`
 - pro Windows: `annotator_gt_tracking_win.py`

Formát výstupu tohoto programu je kompatibilní se vstupem programu `evaluate_tracking.py` pro vyhodnocení trasovacích algoritmů a slouží jako ground truth tras brouků.

### Převodníky
### `convert_boxmot_to_json.py`
Načte výstup z nástroje [BoxMot](https://github.com/mikel-brostrom/boxmot), který poskytuje implementaci různých trasovacích algoritmů a převede jej do požadovaného formátu v JSON souboru. Tento JSON tedy obsahuje výsledky tras všech brouků napříč celým videem.

Spuštění:
```
convert_boxmot_to_json.py

- v záhlaví programu je možné přenastavit vstupní a výstupní cesty

```

Formát výstupu tohoto programu je kompatibilní se vstupem programu `evaluate_tracking.py` pro vyhodnocení trasovacích algoritmů a slouží jako výsledky trasování brouků.

### `convert_json_to_yolo.py`

Načte výstupní JSON anotátoru `annotator_detection.py` a převede jej do formátu anotací pro trénování YOLO detekčního modelu v podobě textových souborů s normalizovanými souřadnicemi pro každý anotovaný snímek.

Spuštění:
```
convert_json_to_yolo.py [-h] -j JSON -o OUTPUT

options:
  -h, --help           vypíše nápovědu k programu
  -j, --json JSON      cesta ke vstupnímu JSON souboru
  -o, --output OUTPUT  cesta k výstupnímu adresáři pro uložení YOLO anotací

```


### Detektor
### `predict.py`
Skript predikuje bounding boxy brouků pomocí zadaného modelu na zadaném snímku a výsledný snímek s predikovanými bounding boxy zobrazí a uloží.

Spuštění:
```
predict.py
```
Veškeré cesty a parametry je nutné změnit přímo ve skriptu.

### `train.py`
Načte předtrénovaný model a spustí dotrénovaní na zadaném datasetu s požadovanými parametry pro trénování. Výstupem je složka s nejlepším modelem best.pt a posledním last.pt. Dále jsou ve složce grafy se statistikou labelů v datasetu, confusion matice, F1 křivka, recall, precision a grafy ukazující hodnoty loss funkce během trénování tyto hodnoty jsou zaznamenány i v results.csv. Také zde nalezneme snímky z vybraných batch z tréninku a z validace.

Spuštění:
```
train.py
```
Veškeré cesty a parametry je nutné změnit přímo ve skriptu.

### `validation.py`
Načte dotrénovaný model a spustí jeho validaci na zadaném datasetu. Vypisováno je recall, precision, mAP@50 a mAP@5090. Také je vytvořena složka s grafy obdobně jako po dotrénování.

Spuštění:
```
validation.py
```
Veškeré cesty a parametry je nutné změnit přímo ve skriptu.

### Trasování
### `beetle_tracker.py`
Načte dotrénovaný model na detekci a začne sledovat trasy brouků pomocí zvoleného algoritmu na zvoleném videu. Je možné si zobrazit aktuální bounding boxy a trasy brouků. Také je možné tento výstup uložit jako video. Primární využití je možnost výstupu tras v JSON formátu, který se následně využívá pro evaluaci algoritmu trasování v `evaluate_tracking.py`.

Ovládání:
```
Klávesy:
  Q       vypnutí aplikace pokud bylo zvoleno --show, uloží korektně výstupní soubory
  Ctrl-C  vypnutí aplikace, uloží korektně výstupní soubory
```

Spuštění:
```
beetle_tracker.py [-h] -v VIDEO [-o OUTPUT] -m MODEL [--show] [--save_video SAVE_VIDEO] [--track_length TRACK_LENGTH] [--botsort] [--bytetrack]

options:

  -h, --help                    vypíše nápovědu k programu
  -v VIDEO, --video VIDEO       cesta k vstupnímu videu
  -o OUTPUT, --output OUTPUT    uloží trasy brouků do zvolené složky ve formátu JSON
  -m MODEL, --model MODEL       cesta k detekčnímu modelu
  --show                        zobrazí okno s detekovanými brouky a jejich trasami při běhu
  --save_video SAVE_VIDEO       uloží video s bounding boxy a trasami do zvolené složky
  --track_length TRACK_LENGTH   změní délku zobrazované trasy brouků, výchozí hodnota je 300 snímků
  --botsort                     zvolení BotSort trackeru
  --bytetrack                   zvolení ByteTrack trackeru
```

### `evaluate_tracking.py`
Vyhodnotí metriky trasování zmiňované v technické zprávě pro zadané ground truth a uloží jej do JSON souboru pro případně další zpracování programem `proccess_tracking_results.py`.

Vstup:

* Složka s vytvořenými vstupními ground truth soubory je dostupná v adresáři `dataset_ground_truth_tracks/`, složka s již vygenerovánými výstupy jednotlivých trasovacích algoritmů jsou ve složce `tracking_results/` na [Google Drive](https://drive.google.com/drive/folders/10Eu2y_Ief9yyekn0N4Fv8GMXV4uJlnSl?usp=sharing).

Výstup:

* Příklad výstupů tohoto programu je umístěn ve složce `tracking_eval_results/` na [Google Drive](https://drive.google.com/drive/folders/10Eu2y_Ief9yyekn0N4Fv8GMXV4uJlnSl?usp=sharing).

Spuštění:
```
evaluate_tracking.py

- v záhlaví programu je možné přenastavit vstupní a výstupní cesty
```

### `proccess_tracking_results.py`

Pro všechny vyhodnocené trasovací algoritmy ve zvolené složce (výstupy z programu `evaluate_tracking.py`) vypíše tabulku s výslednými metrikami v LaTeX formátu a uloží graf vyobrazující, jak si jednotlivé sledovací algoritmy vedly u obtížných ground truth tras.

Spuštění:
```
proccess_tracking_results.py

- v záhlaví programu je možné přenastavit vstupní a výstupní cesty
```

### Zpracování videa

### `crop_video_images.py`
Vytvoří zadaný počet čtvercových výstřižků z původních videozáznamů brouků o zadaném rozlišení. Výběr videa, snímku a umístění čtvercového výřezu je proveden náhodně. Výsledné výstřižky uloží do zvoleného adresáře ve formátu JPG. Slouží jako zdroj snímků pro anotaci pomocí nástroje `annotator_detection.py`.

Vyžaduje přítomnost složky `BuoT/` s původními videi v kořenovém adresáři (dostupné ve složce `original_videos/` na [Google Drive](https://drive.google.com/drive/folders/10Eu2y_Ief9yyekn0N4Fv8GMXV4uJlnSl?usp=sharing)).

Spuštění:
```
cropVideoImages.py [-h] -r RESOLUTION -d DIRECTORY -n NUMBER

options:
  -h, --help                  vypíše nápovědu k programu
  -r, --resolution RESOLUTION velikost výsledných výstřižků v pixelech
  -d, --directory DIRECTORY   cesta k výstupnímu adresáři pro uložení výstřižků
  -n, --number NUMBER         počet vygenerovaných výstřižků
```

### `video_splitter.py`

Rozdělí zadané video na segmenty podle zvoleného počtu snímků a uloží je v podobě kratších MP4 záznamů do výstupního adresáře. Slouží k vytvoření menších vstupních videí pro anotování tras v nástroji `annotator_gt_tracking.py` pro jeho lepší výkonnost.


```
videoSplitter.py [-h] -v VIDEO [-d DIRECTORY] [-s SEGMENT] [-int START END]

options:
  -h, --help                  vypíše nápovědu k programu
  -v, --video VIDEO           cesta ke vstupnímu videu
  -d, --directory DIRECTORY   cesta k výstupnímu adresáři pro uložení části videa
  -s, --segment SEGMENT       počet snímků podle kterého je původní video rozděleno
  -int, --interval START END  čísla segmentů které mají být uloženy (interval)
```