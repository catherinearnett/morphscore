import pandas as pd
import numpy as np
import os
import tarfile
import zipfile
import glob

from transformers import AutoTokenizer
from transformers import PreTrainedTokenizerFast

def morph_eval(morphemes, tokens): #returns -1,0, 1
    point = -1
    if len(tokens) == 1:
        point = 0
    else:
        segment_score = 0
        for t in range(len(tokens)-1):
            pt1 = ''.join(tokens[:t+1])
            rest = ''.join(tokens[t+1:])
            segments = [pt1, rest]
            if segments == morphemes:
                segment_score += 1
            else:
                segment_score += 0
        if segment_score == 1:
            point = 1
        else:
            point = -1
    return point

def get_morphscore(language, tokenizer):
    dataset = pd.read_csv(f'C:/Users/cathe/tokenizer_typology/final_morphscore/{language}_morph_data.csv')
    points = []
    for d in range(len(dataset)):
        pt1 = dataset.iloc[d]['pt1']
        rest = dataset.iloc[d]['rest']
        morphemes = [pt1, rest]
        full_word = dataset.iloc[d]['full_word']
        tokens = tokenizer(full_word)['input_ids']

        vocab_size = tokenizer.vocab_size
        spc_tok1 = int(vocab_size)
        spc_tok2 = int(vocab_size) + 1
        if spc_tok1 in tokens:
            tokens.remove(spc_tok1)
        if spc_tok2 in tokens:
            tokens.remove(spc_tok2)

        tokens = [tokenizer.decode(t) for t in tokens]
        point = morph_eval(morphemes, tokens)

        points.append(point)

    points = [x for x in points if x != 0]
    points= [0 if x == -1 else x for x in points]
    morph_score = np.mean(points)
    return morph_score

languages = {
            'bulgarian': ['bul_cyrl', 'bg'],
            'english': ['eng_latn', 'en'],
             'spanish': ['spa_latn', 'es'],
            'greek': ['ell_grek', 'el'],
             'persian': ['pes_arab', 'fa'],
             'japanese': ['jpn_jpan', 'ja'],
             'korean': ['kor_hang', 'ko'],
             'turkish': ['tur_latn', 'tr'],
             'indonesian': ['ind_latn', 'id'],
             'hungarian': ['hun_latn', 'hu'],
            'urdu': ['urd_arab', 'ur'],
            'slovenian': ['slv_latn', 'sl'],
             'tamil': ['tam_taml', 'ta'],
             'georgian': ['kat_geor', 'ka'],
             'armenian': ['hye_armn', 'hy'],
             'irish': ['gle_latn', 'ga'],
             'icelandic': ['isl_latn'],
             'gujarati': ['guj_gujr', 'gu'],
             'kurdish': ['kmr_latn', 'ku'],
             'cebuano': ['ceb_latn', 'ceb'],
             'basque': ['eus_latn', 'eu'],
             'zulu': ['zul_latn', 'zul_latn']
                }

results = pd.DataFrame(columns = ['language', 'lang_name', 'tok_lines', 'morph_score'])

results.to_csv('com_tokenizers_morphscore.csv', mode='w', header=True)

for l in languages:
    lang_code = languages[l][0]
    tok_lang_code = languages[l][1]

    tokenizer_path = f'tokenizers/{tok_lang_code}_10k'
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, use_fast = False)

    morphscore = get_morphscore(l, tokenizer)
    new_line = pd.DataFrame({
            'language': [lang_code],
            'lang_name': [l],
            'tok_lines': ['10k'],
            'morph_score': [morphscore]
    })
    new_line.to_csv('com_tokenizers_morphscore.csv', mode='a', header=False)
    print(new_line)
