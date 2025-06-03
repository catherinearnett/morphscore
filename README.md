# MorphScore

MorphScore is a tokenizer evaluation framework, which evaluates the extent to which a tokenizer segments words along morpheme boundaries. This repository contains datasets to evaluate tokenization for 22 languages (see table below). 

For details on v1 of MorphScore, see the main branch. The original version is described in our [COLING paper](https://aclanthology.org/2025.coling-main.441/). All code and data used in the original paper are available on [OSF](https://osf.io/jukzd/?view_only=3d0d491d24074215a0ab81f72a693c16). 

## How to Use MorphScore v2

Clone the repo and import `MorphScore`.

```
from morphscore.morphscore import MorphScore
```

Load a Hugging-Face-compatible tokenizer.

```
tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-2-7b')
```

These are the default settings we recommend based on the forthcoming preprint. Language codes should be in the format ISO 639-3 code + '_' + ISO 15924 code, e.g. `eng_latn'. The list of languages and their codes is provided in the table below. If `return_df=True`, the scoring function will generate a by-item dataframe that enables more fine-grained analysis. 

```
 morph_score = MorphScore(language_subset=['eng_latn'], # if empty, will run on all languages
                             by_split=False, 
                             freq_scale=True,
                             exclude_single_tok=False)
 result, df = morph_score.eval(tokenizer, return_df=True)

```

The main metrics returned in `result` are:

* `morphscore_recall`: recall
* `morphscore_precision`: precision
* `morphscore_recall_std`: standard deviation of recall metric
* `morphscore_precision_std`: standard deviation of precision metric
* `num_samples`: number of items after filtering for a given language and given the parameters in the scoring function.
* `mean_token_char_ratio`: the mean number of tokens that a given tokenizer segments the items in the dataset into, divided by the word length in characters. This helps identify cases of oversegmentation.


## Changes for v2

Many aspects of MorphScore have changed in v2, though the general concept is still the same. 

### Additional Metadata

In this version, we add POS, full-sentence context, and morphological analysis, e.g. number.

### Selecting Boundaries
In MorphScore v1, the boundary was determined by taking the segmentation in UD. Only if the segmentation had exactly one boundary and both parts added up to make up the full word form was it added. In the updated version, we determine a stem as the substring of the full word form also contained in the lemma. 

```
stem = full_word - lemma
```

### Multiple Boundaries 

We allow for multiple boundaries. We determine the boundaries by splitting the word form based on the stem. So there are up to two boundaries. There is a part preceding the stem and a part following the stem. Either of these may be empty, meaning there may be only one boundary.

### Multiple Sources

In this version, to maximize dataset size, we pull from at least one UD treebank and all splits (train, dev, test). The dataset sources and train splits are in the dataset, so you can easily remove datasets or splits as desired.

## Scoring

First, filter [clean datasets](https://huggingface.co/datasets/catherinearnett/morphscore), as not all instances will be used.
*  only keep `unique` == 'unique'
*  only keep cases where `lemma` == `stem` (this excludes potential cases where the `stem = full_word - lemma` leads to invalid segmentations; this is how MorphScore v1 worked)

Default scoring:
*  exclude single-token words
*  `1` indicates that there exists a token boundary at every morpheme boundary (up to 2 per word). If only one overlaps, score is `0.5`.

Alternative scoring options:
*  allow for breakdown of score by POS
*  allow for scores to only come from certain splits, e.g. `test`
*  allow scores to be scaled by word frequency
*  allow for single-token words to be scored as correct

## Datasets

Clean datasets are on Hugging Face: https://huggingface.co/datasets/catherinearnett/morphscore. 

### Dataset Structure:

* `language`: [ISO 639-3](https://en.wikipedia.org/wiki/ISO_639-3) and [ISO 15924](https://en.wikipedia.org/wiki/ISO_15924) codes joined with an underscore, 
e.g. 'abk_cyrl'
*  `dataset_source`: name of the UD treebank, e.g. 'UD_Abkhaz-AbNC'
*  `data_split`: train, dev, test
*  `wordform`: whole word, as it appears in the sentence (incl. capitalization)
*  `unique`: the first occurence of a wordform in the UD dataset is labelled `unique` and all subsequent instances are labelled `repeat`
*  `lemma`: lemma
*  `stem`: as defined above
*  `preceding_part`: part to the left of the stem
*  `following_part`: part to the right of the stem
*  `pos`: part of speech, as labelled in UD
*  `morph_comp`: information about morphological features, e.g. number, gender, tense
*  `sentence`: sentence in which word occurs
*  `sentence_id`: sentence ID from treebank
*  `word_freq`: number of occurrences of a wordform in the entire UD dataset for that language
*  `word_freq_norm`: `word_freq` normalized by the total number of words in the corpus, excluding punctuation.

### Dataset Sources and Stats

These include ones where `stem` != `lemma`.

| **Language** | **ISO 639-3** | **ISO 15924** | **Num. Words** | **Num. Unique Words** | **Data Source(s)** | 
|--------------|---------------|---------------|-----------------|-----------------------|---------------------|
| Example      | exa           | exam          | 1000            | 1000                  | [UD Source 1] [UD Source 2] [UniMorph Source] |
| Arabic       | arb           | arab          | 197112          | 19126                 | [UD_Arabic-PADT](https://github.com/UniversalDependencies/UD_Arabic-PADT/tree/master) |
| English      | eng           | latn          | 31039           | 5844                  | [UD_English-EWT](https://github.com/UniversalDependencies/UD_English-EWT/tree/master) |
| German       | deu           | latn          | 949279          | 49239                 | [UD_German-HDT](https://github.com/UniversalDependencies/UD_German-HDT/tree/master) |
| Russian      | rus           | cyrl          | 590060          | 105749                | [UD_Russian-SynTagRus](https://github.com/UniversalDependencies/UD_Russian-SynTagRus/tree/master) |
| Turkish      | tur           | latn          | 71984           | 32587                 | [UD_Turkish-Kenet](https://github.com/UniversalDependencies/UD_Turkish-Kenet/tree/master) |
| Abkhaz       | abk           | cyrl          | 4518            | 3222                  | [UD_Abkhaz-AbNC](https://github.com/UniversalDependencies/UD_Abkhaz-AbNC/tree/master) |
| Afrikaans    | afr           | latn          | 7011            | 2093                  | [UD_Afrikaans-AfriBooms](https://github.com/UniversalDependencies/UD_Afrikaans-AfriBooms/tree/master) |
| Albanian     | sqi (tos)     | latn          | 897             | 702                   | [UD_Albanian-STAF](https://github.com/UniversalDependencies/UD_Albanian-STAF) |
| Amharic      | amh           | ethi          | 39              | 9                     | [UD_Amharic-ATT](https://github.com/UniversalDependencies/UD_Amharic-ATT) |
| Armenian     | hye           | armn          | 18906           | 8994                  | [UD_Armenian-ArmTDP](https://github.com/UniversalDependencies/UD_Armenian-ArmTDP/tree/master) |
| Azerbaijani  | aze           | latn          | 368             | 251                   | [UD_Azerbaijani-TueCL](https://github.com/UniversalDependencies/UD_Azerbaijani-TueCL) |
| Bambara      | bam           | latn          | 6849            | 665                   | [UD_Bambara-CRB](https://github.com/UniversalDependencies/UD_Bambara-CRB) |
| Basque       | eus           | latn          | 50901           | 15932                 | [UD_Basque-BDT](https://github.com/UniversalDependencies/UD_Basque-BDT) |
| Belarusian   | bel           | cyrl          | 104096          | 31129                 | [UD_Belarusian-HSE](https://github.com/UniversalDependencies/UD_Belarusian-HSE/tree/master) |
| Bengali      | ben           | beng          | 102             | 67                    | [UD_Bengali-BRU](https://github.com/UniversalDependencies/UD_Bengali-BRU) |
| Bhojpuri     | bho           | deva          | 1371            | 360                   | [UD_Bhojpuri-BHTB](https://github.com/UniversalDependencies/UD_Bhojpuri-BHTB) |
| Breton       | bre           | latn          | 3054            | 1021                  | [UD_Breton-KEB](https://github.com/UniversalDependencies/UD_Breton-KEB) |
| Bulgarian    | bul           | cyrl          | 44412           | 15468                 | [UD_Bulgarian-BTB](https://github.com/UniversalDependencies/UD_Bulgarian-BTB) |
| Buriat/Buryat| bur           | cyrl          | 3646            | 2322                  | [UD_Buryat-BDT](https://github.com/UniversalDependencies/UD_Buryat-BDT) |
| Cantonese/Yue Chinese| yue   | hant          | 42              | 13                    | [UD_Cantonese-HK](https://github.com/UniversalDependencies/UD_Cantonese-HK) |
| Catalan      | cat           | latn          | 15495           | 3385                  | [UD_Catalan-AnCora](https://github.com/UniversalDependencies/UD_Catalan-AnCora) |
| Cebuano      | ceb           | latn          | 264             | 136                   | [UD_Cebuano-GJA](https://github.com/UniversalDependencies/UD_Cebuano-GJA) |
| Mandarin Chinese  | zho/cmn  | hans          | 915             | 140                   | [UD_Chinese-GSDSimp](https://github.com/UniversalDependencies/UD_Chinese-GSDSimp) |
| Croatian     | hrv           | latn          | 75681           | 23363                 | [UD_Croatian-SET](https://github.com/UniversalDependencies/UD_Croatian-SET) |
| Czech        | ces           | latn          | 200387          | 44025                 | [UD_Czech-CAC](https://github.com/UniversalDependencies/UD_Czech-CAC/tree/master) |
| Danish       | dan           | latn          | 25662           | 8256                  | [UD_Danish-DDT](https://github.com/UniversalDependencies/UD_Danish-DDT) |
| Dutch        | nld           | latn          | 42900           | 12512                 | [UD_Dutch-Alpino](https://github.com/UniversalDependencies/UD_Dutch-Alpino/tree/master) |
| Erzya        | myv           | cyrl          | 8147            | 4826                  | [UD_Erzya-JR](https://github.com/UniversalDependencies/UD_Erzya-JR) |
| Estonian     | est           | latn          | 199597          | 62170                 | [UD_Estonian-EDT](https://github.com/UniversalDependencies/UD_Estonian-EDT) |
| Finnish      | fin           | latn          | 99308           | 41095                 | [UD_Finnish-TDT](https://github.com/UniversalDependencies/UD_Finnish-TDT/tree/master) |
| French       | fra           | latn          | 103887          | 13508                 | [UD_French-GSD](https://github.com/UniversalDependencies/UD_French-GSD) |
| Galician     | glg           | latn          | 29484           | 7113                  | [UD_Galician-CTG](https://github.com/UniversalDependencies/UD_Galician-CTG) |
| Georgian     | kat           | geor          | 20148           | 8622                  | [UD_Georgian-GLC](https://github.com/UniversalDependencies/UD_Georgian-GLC) |
| Modern Greek | ell           | grek          | 21428           | 6986                  | [UD_Greek-GDT](https://github.com/UniversalDependencies/UD_Greek-GDT/tree/master) |
| Gujarati     | guj           | gujr          | 120             | 81                    | [UD_Gujarati-GujTB](https://github.com/UniversalDependencies/UD_Gujarati-GujTB/tree/master) |
| Haitian Creole| hat          | latn          | 950             | 37                    | [UD_Haitian_Creole-Adolphe](https://github.com/UniversalDependencies/UD_Haitian_Creole-Adolphe) |
| Hebrew       | heb           | hebr          | 43102           | 9768                  | [UD_Hebrew-HTB](https://github.com/UniversalDependencies/UD_Hebrew-HTB) |
| Hindi        | hin           | deva          | 83865           | 4749                  | [UD_Hindi-HDTB](https://github.com/UniversalDependencies/UD_Hindi-HDTB) |
| Hungarian    | hun           | latn          | 12349           | 8103                  | [UD_Hungarian-Szeged](https://github.com/UniversalDependencies/UD_Hungarian-Szeged) |
| Icelandic    | isl           | latn          | 329620          | 40686                 | [UD_Icelandic-IcePaHC](https://github.com/UniversalDependencies/UD_Icelandic-IcePaHC)|
| Indonesian   | ind           | latn          | 16844           | 3400                  | [UD_Indonesian-GSD](https://github.com/UniversalDependencies/UD_Indonesian-GSD) |
| Irish        | gle           | latn          | 31911           | 7474                  | [UD_Irish-IDT](https://github.com/UniversalDependencies/UD_Irish-IDT/tree/master) |
| Italian      | ita           | latn          | 73790           | 10981                 | [UD_Italian-ISDT](https://github.com/UniversalDependencies/UD_Italian-ISDT/tree/master) |
| Japanese     | jpn           | jpan          | 16898           | 5427                  | [UD_Japanese-GSDLUW](https://github.com/UniversalDependencies/UD_Japanese-GSDLUW) |
| Kazakh       | kaz           | cyrl          | 4200            | 2738                  | [UD_Kazakh-KTB](https://github.com/UniversalDependencies/UD_Kazakh-KTB) |
| Komi-Zyrian  | kpv           | cyrl          | 2670            | 2017                  | [UD_Komi_Zyrian-Lattice](https://github.com/UniversalDependencies/UD_Komi_Zyrian-Lattice) |
| Korean       | kor           | hang          | 239862          | 86349                 | [UD_Korean-Kaist](https://github.com/UniversalDependencies/UD_Korean-Kaist) |
| Kirghiz/Kyrgyz| kir          | cyrl          | 11752           | 4659                  | [UD_Kyrgyz-KTMU](https://github.com/UniversalDependencies/UD_Kyrgyz-KTMU) |
| Latvian      | lav           | latn          | 141550          | 40081                 | [UD_Latvian-LVTB](https://github.com/UniversalDependencies/UD_Latvian-LVTB/tree/master) |
| Lithuanian   | lit           | latn          | 32378           | 13140                 | [UD_Lithuanian-ALKSNIS](https://github.com/UniversalDependencies/UD_Lithuanian-ALKSNIS) |
| Macedonian   | mkd           | cyrl          | 285             | 241                   | [UD_Macedonian-MTB](https://github.com/UniversalDependencies/UD_Macedonian-MTB) |
| Malayalam    | mal           | mlym          | 867             | 710                   | [UD_Malayalam-UFAL](https://github.com/UniversalDependencies/UD_Malayalam-UFAL) |
| Manx         | glv           | latn          | 2299            | 873                   | [UD_Manx-Cadhan](https://github.com/UniversalDependencies/UD_Manx-Cadhan) |
| Marathi      | mar           | deva          | 1610            | 663                   | [UD_Marathi-UFAL](https://github.com/UniversalDependencies/UD_Marathi-UFAL) |
| Moksha       | mdf           | cyrl          | 1733            | 1401                  | [UD_Moksha-JR](https://github.com/UniversalDependencies/UD_Moksha-JR) |
| Northern Sami| sme           | latn          | 10360           | 5024                  | [UD_North_Sami-Giella](https://github.com/UniversalDependencies/UD_North_Sami-Giella) |
| Norwegian    | nob           | latn          | 87394           | 15716                 | [UD_Norwegian-Bokmaal](https://github.com/UniversalDependencies/UD_Norwegian-Bokmaal) |
| Occitan      | oci           | latn          | 6751            | 2561                  | [UD_Occitan-TTB](https://github.com/UniversalDependencies/UD_Occitan-TTB) |
| Pashto       | pus           | arab          | 779             | 351                   | [UD_Pashto-Sikaram](https://github.com/UniversalDependencies/UD_Pashto-Sikaram) |
| Persian      | fas           | arab          | 102374          | 14847                 | [UD_Persian-PerDT](https://github.com/UniversalDependencies/UD_Persian-PerDT) |
| Polish       | pol           | latn          | 131836          | 42545                 | [UD_Polish-PDB](https://github.com/UniversalDependencies/UD_Polish-PDB/tree/master) |
| Portuguese   | por           | latn          | 69430           | 13074                 | [UD_Portuguese-CINTIL](https://github.com/UniversalDependencies/UD_Portuguese-CINTIL) |
| Romanian     | ron           | latn          | 72968           | 19108                 | [UD_Romanian-RRT](https://github.com/UniversalDependencies/UD_Romanian-RRT) |
| Sanskrit     | san           | deva          | 144583          | 32671                 | [UD_Sanskrit-Vedic](https://github.com/UniversalDependencies/UD_Sanskrit-Vedic) |
| Scottish Gaelic | gla        | latn          | 27181           | 3495                  | [UD_Scottish_Gaelic-ARCOSG](https://github.com/UniversalDependencies/UD_Scottish_Gaelic-ARCOSG) |
| Serbian      | srp           | latn          | 37324           | 12278                 | [UD_Serbian-SET](https://github.com/UniversalDependencies/UD_Serbian-SET/tree/master) |
| Sindhi       | snd           | arab          | 3584            | 1132                  | [UD_Sindhi-Isra](https://github.com/UniversalDependencies/UD_Sindhi-Isra/tree/master) |
| Sinhala      | sin           | sinh          | 354             | 284                   | [UD_Sinhala-STB](https://github.com/UniversalDependencies/UD_Sinhala-STB) |
| Slovak       | slk           | latn          | 35545           | 16169                 | [UD_Slovak-SNK](https://github.com/UniversalDependencies/UD_Slovak-SNK) |
| Slovenian    | slv           | latn          | 93048           | 32134                 | [UD_Slovenian-SSJ](https://github.com/UniversalDependencies/UD_Slovenian-SSJ) |
| Spanish      | spa           | latn          | 134449          | 17341                 | [UD_Spanish-AnCora](https://github.com/UniversalDependencies/UD_Spanish-AnCora) |
| Swedish      | swe           | latn          | 29514           | 8135                  | [UD_Swedish-LinES](https://github.com/UniversalDependencies/UD_Swedish-LinES) |
| Tagalog      | tgl           | latn          | 212             | 78                    | [UD_Tagalog-Ugnayan](https://github.com/UniversalDependencies/UD_Tagalog-Ugnayan) |
| Tamil        | tam           | taml          | 4499            | 2178                  | [UD_Tamil-TTB](https://github.com/UniversalDependencies/UD_Tamil-TTB) |
| Tatar        | tat           | cyrl          | 899             | 708                   | [UD_Tatar-NMCTT](https://github.com/UniversalDependencies/UD_Tatar-NMCTT/tree/master) |
| Ukrainian    | ukr           | cyrl          | 44288           | 21584                 | [UD_Ukrainian-IU](https://github.com/UniversalDependencies/UD_Ukrainian-IU) |
| Urdu         | urd           | arab          | 30825           | 2450                  | [UD_Urdu-UDTB](https://github.com/UniversalDependencies/UD_Urdu-UDTB/tree/master) |
| Uighur/Uyghur| uig           | arab          | 10427           | 3969                  | [UD_Uyghur-UDT](https://github.com/UniversalDependencies/UD_Uyghur-UDT) |
| Uzbek        | uzb           | latn          | 2466            | 1934                  | [UD_Uzbek-UT](https://github.com/UniversalDependencies/UD_Uzbek-UT) |
| Veps         | vep           | latn          | 598             | 399                   | [UD_Veps-VWT](https://github.com/UniversalDependencies/UD_Veps-VWT) |
| Vietnamese   | vie           | latn          | 32              | 29                    | [UD_Vietnamese-VTB](https://github.com/UniversalDependencies/UD_Vietnamese-VTB/tree/master) |
| Welsh        | cym           | latn          | 11781           | 2860                  | [UD_Welsh-CCG](https://github.com/UniversalDependencies/UD_Welsh-CCG) |
| Wolof        | wol           | latn          | 9211            | 1734                  | [UD_Wolof-WTB](https://github.com/UniversalDependencies/UD_Wolof-WTB/tree/master) |
| Yakut        | sah           | cyrl          | 479             | 330                   | [UD_Yakut-YKTDT](https://github.com/UniversalDependencies/UD_Yakut-YKTDT) |
| Latgalian    | ltg           | latn          | 69              | 63                    | [UD_Latgalian-Cairo](https://github.com/UniversalDependencies/UD_Latgalian-Cairo) |
| Ligurian     | lij           | latn          | 1318            | 637                   | [UD_Ligurian-GLT](https://github.com/UniversalDependencies/UD_Ligurian-GLT/tree/master) |
| Upper Sorbian| hsb           | latn          | 3797            | 2498                  | [UD_Upper_Sorbian-UFAL](https://github.com/UniversalDependencies/UD_Upper_Sorbian-UFAL) |

## How to Cite

```

@misc{arnett2025alignment,
  author = {Arnett, Catherine and Hudspeth, Marisa and O'Connor, Brendan},
  title = {{Evaluating Morphological Alignment of Tokenizers in 70 Languages}},
  year = {2025},
  note = {Preprint}
}


@inproceedings{arnett-bergen-2025-language,
    title = "Why do language models perform worse for morphologically complex languages?",
    author = "Arnett, Catherine  and
      Bergen, Benjamin",
    editor = "Rambow, Owen  and
      Wanner, Leo  and
      Apidianaki, Marianna  and
      Al-Khalifa, Hend  and
      Eugenio, Barbara Di  and
      Schockaert, Steven",
    booktitle = "Proceedings of the 31st International Conference on Computational Linguistics",
    month = jan,
    year = "2025",
    address = "Abu Dhabi, UAE",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.coling-main.441/",
    pages = "6607--6623"
}
```
