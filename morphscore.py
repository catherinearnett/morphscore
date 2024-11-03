import pandas as pd
import numpy as np

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
    dataset = pd.read_csv(f'data/{language}_morph_data.csv')
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
