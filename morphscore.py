import pandas as pd
import numpy as np

def morph_eval(morphemes, tokens):
    """
    Returns 1 if the morphemes are correctly segmented by the tokenizer,
    0 if they are not segmented correctly, and -1 if the full word is already
    present in the tokenizer's vocabulary.
    """
    if len(tokens) == 1:
        return -1
    for t in range(len(tokens)-1):
        pt1 = ''.join(tokens[:t+1])
        rest = ''.join(tokens[t+1:])
        segments = [pt1, rest]
        if segments == morphemes:
            return 1
    return 0

def get_morphscore(language, tokenizer):
    dataset = pd.read_csv(f'morphscore/data/{language}_morph_data.csv')
    points = []
    for d in range(len(dataset)):
        pt1 = dataset.iloc[d]['pt1']
        rest = dataset.iloc[d]['rest']
        morphemes = [pt1, rest]
        full_word = dataset.iloc[d]['full_word']
        tokens = tokenizer(full_word, add_special_tokens=False)['input_ids']
        tokens = [tokenizer.decode(t) for t in tokens]

        # Remove special prefixes added by common tokenizers like BPE or Wordpiece
        tokens = [token.strip('_').strip('Ġ').strip('##').strip() for token in tokens]
        tokens = [token for token in tokens if token != '']
        
        # Compare gold morphemes with tokenizer tokens for alignment
        point = morph_eval(morphemes, tokens)
        points.append(point)

    # Skip words if they are already included in the tokenizer's vocabulary
    points = [x for x in points if x != -1]
    morph_score = np.mean(points)
    return morph_score
