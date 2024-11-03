# MorphScore

MorphScore is a tokenizer evaluation framework, which evaluates the extent to which a tokenizer segments words along morpheme boundaries. This repository contains datasets to evaluate tokenization for 22 languages (see table below). 

See the preprint for full methodological details. All code and data used in the original paper are available on [OSF](https://osf.io/jukzd/?view_only=3d0d491d24074215a0ab81f72a693c16). 

| **Language** | **ISO 639-3** | **ISO 15924** | **Lang. Family** | **Morph. Type** | **Num. Items** |
|--------------|---------------|---------------|------------------|-----------------|----------------|
| Armenian     | hye           | armn          | Indo-European    | agglutinative   | 2000           |
| Basque       | eus           | latn          | Basque           | agglutinative   | 2000           |
| Bulgarian    | bul           | cyrl          | Indo-European    | fusional        | 2000           |
| Cebuano      | ceb           | latn          | Austronesian     | agglutinative   | 131            |
| English      | eng           | latn          | Indo-European    | fusional        | 2000           |
| Georgian     | kat           | geor          | Kartvelian       | agglutinative   | 200            |
| Greek        | ell           | grek          | Indo-European    | fusional        | 112            |
| Gujarati     | guj           | gujr          | Indo-European    | fusional        | 547            |
| Hungarian    | hun           | latn          | Uralic           | agglutinative   | 2000           |
| Icelandic    | isl           | latn          | Indo-European    | fusional        | 1852           |
| Indonesian   | ind           | latn          | Austronesian     | agglutinative   | 1552           |
| Irish        | gle           | latn          | Indo-European    | fusional        | 1877           |
| Japanese     | jpn           | jpan          | Japonic          | agglutinative   | 2000           |
| Korean       | kor           | hang          | Koreanic         | agglutinative   | 2000           |
| Northern Kurdish  | kmr      |    latn       | Indo-European    | fusional        | 319            |
| Persian      | pes           | arab          | Indo-European    | fusional        | 2000           |
| Slovenian    | slv           | latn          | Indo-European    | fusional        | 2000           |
| Spanish      | spa           | latn          | Indo-European    | fusional        | 2000           |
| Tamil        | tam           | taml          | Dravidian        | agglutinative   | 884            |
| Turkish      | tur           | latn          | Turkic           | agglutinative   | 2000           |
| Urdu         | urd           | arab          | Indo-European    | fusional        | 1649           |
| Zulu         | zul           | latn          | Niger-Congo      | agglutinative   | 2000           |

## Calculating MorphScore

To evaluate a tokenizer's MorphScore for each word in a test set, we assign a value of `1` if the tokenizer places a token boundary at the morpheme boundary of interest, regardless of other token boundaries. We assign a value of `0` if there is not a token boundary at the morpheme boundary of interest.  We exclude items which contain no token boundaries (i.e. the entire word form is in the tokenizer's vocabulary), so as not to penalize the tokenizer for not segmenting the word. MorphScore is the mean of the assigned values across the dataset for a given language.

Example scores for different segmentations:

| **Language**   | **Word**       | **Source**   | **Segmentation**                 | **Score** |
|----------------|----------------|--------------|----------------------------------|-----------|
| **Basque**     | aldiz          | morphemic    | aldi + z                         |           |
|                |                | Tokenizer 1  | [`al`, `diz`]                   | 0         |
|                |                | Tokenizer 2  | [`aldi`, `z`]                   | 1         |
| **Croatian**   | suučesnika     | morphemic    | suučesnik + a                   |           |
|                |                | Tokenizer 1  | [`su`, `uče`, `s`, `nika`]      | 0         |
|                |                | Tokenizer 2  | [`su`, `u`, `če`, `s`, `nika`]  | 0         |
| **Icelandic**  | samráðs        | morphemic    | samráð + s                      |           |
|                |                | Tokenizer 1  | [`samráð`, `s`]                 | 1         |
|                |                | Tokenizer 2  | [`samráðs`]                     | exclude   |
| **Greek**      | Αδριανής       | morphemic    | Αδριανή + ς                      |           |
|                |                | Tokenizer 1  | [`Α`, `δ`, `ριανής`]            | 0         |
|                |                | Tokenizer 2  | [`Α`, `δρ`, `ιανή`, `ς`]        | 1         |

## How to Use

This tool requires `numpy` and `pandas` to be installed.

Tested in Python 3.10.

First, clone the repository:

```
git clone https://github.com/catherinearnett/morphscore.git
```

Then import the morphscore function:

```
from morphscore import get_morphscore
```

Load a tokenizer:

```
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained('facebook/xglm-7.5B')
```

Use the language name as written in the following list: `bulgarian`, `english`, `spanish`, `greek`, `persian`, `japanese`, `korean`, `turkish`, `indonesian`, `hungarian`, `urdu`, `slovenian`, `tamil`, `georgian`, `armenian`, `irish`, `icelandic`, `gujarati`, `kurdish`, `cebuano`, `basque`, `zulu`.

```
print(get_morphscore(language, tokenizer))
```

# How to Cite
```
@misc{arnett2024morph,
  author = {Arnett, Catherine and Bergen, Benjamin K.},
  title = {{Why do language models perform worse for morphologically complexlanguages?}},
  year = {2024},
  eprint = {arXiv:},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/pdf/},
  note = {Preprint}
}
```
