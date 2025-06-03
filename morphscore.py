import pandas as pd
import numpy as np
import json
import argparse
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import os
class MorphScore:

    def __init__(self, config_path: Optional[str] = None, **kwargs):
        """
        Initialize MorphScore evaluator.
        
        Args:
            config_path: Path to JSON config file (optional)
            **kwargs: Direct configuration arguments that override defaults/config
        """
        # Set defaults
        self.config = {
            # by default, run on all languages in data_dir
            'data_dir': 'clean_datasets/',

            # Filtering flags
            'unique_only': True,
            'stem_eq_lemma': True,
            'exclude_numbers': True,
            'language_subset': [], # if not empty, run on this subset of languages only
            'splits': ['train', 'dev', 'test'],
            
            # Scoring flags
            'freq_scale': False,    # scale scoring by word frequency
            'exclude_single_tok': True, # exclude single token words from scoring
            'exclude_single_morpheme': True, # exclude single morpheme words from scoring
            'single_tok_point': 1,  # if exclude_single_tok is False, this is the score for single token words
            'correct_point': 1,     # all morpheme boundaries must be correct
            'partial_point': 0.5,   # only one morpheme boundary is correct
            
            # Breakdown flags
            'by_split': False,
            'by_pos': False,

            # tokenizer settings
            'subword_prefix': '' # prefix for subwords, e.g. '##' for wordpiece
        }
        
        # Load config file if provided
        if config_path:
            self._load_config(config_path)
        
        # Override with any direct arguments
        self.config.update(kwargs)
        
        # Validate configuration
        self._validate_config()
    
    def _load_config(self, config_path: str):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
            self.config.update(file_config)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def _validate_config(self):
        """Validate configuration parameters."""
        # Validate point values
        if not isinstance(self.config['single_tok_point'], (int, float)):
            raise ValueError("single_tok_point must be numeric")
        if not isinstance(self.config['correct_point'], (int, float)):
            raise ValueError("correct_point must be numeric")
        if not isinstance(self.config['partial_point'], (int, float)):
            raise ValueError("partial_point must be numeric")
        
        # Validate lists
        if not isinstance(self.config['language_subset'], list):
            raise ValueError("language_subset must be a list")
        if not isinstance(self.config['splits'], list):
            raise ValueError("splits must be a list")
    
    def morph_eval(self, morphemes: List[str], tokens: List[str]) -> float:
        """
        Evaluate morphological segmentation for a single word.
        
        Args:
            morphemes: Ground truth morpheme segmentation [preceding_part, stem, following_part],
                where preceding_part and following_part are optional
            tokens: Tokenizer output segments
            
        Returns:
            tuple: (morphscore_recall_point, morphscore_precision_point)
        """
        if len(tokens) == 1:
            return (np.nan, np.nan) if self.config['exclude_single_tok'] else (self.config['single_tok_point'], self.config['single_tok_point']) 
        
        # find indices of predicted morpheme boundaries
        all_pred_boundaries = []
        idx = 0
        for t in range(len(tokens)):
            tok = tokens[t]
            this_idx = idx + len(tok)
            all_pred_boundaries.append(this_idx)
            idx = this_idx
        
        
        # find index of the gold morpheme boundary and score
        if len(morphemes) == 2: # only 1 gold morpheme boundary
            gold_boundary_idx = len(morphemes[0])
            if gold_boundary_idx in all_pred_boundaries:
                return self.config['correct_point'], 1 / len(all_pred_boundaries)
            else:
                return 0, 0

        elif len(morphemes) == 3:
            gold_boundary_indices = [len(morphemes[0]), len(morphemes[0]) + len(morphemes[1])]

            # if both boundaries are in the predicted boundaries, score is correct
            if gold_boundary_indices[0] in all_pred_boundaries and gold_boundary_indices[1] in all_pred_boundaries:
                return self.config['correct_point'], 2 / len(all_pred_boundaries)
            # if one boundary is in the predicted boundaries, score is partial
            elif gold_boundary_indices[0] in all_pred_boundaries or gold_boundary_indices[1] in all_pred_boundaries:
                return self.config['partial_point'], 1 / len(all_pred_boundaries)
            else:
                return 0, 0
        
        # number of gold morphemes is 1
        else:
            if self.config['exclude_single_morpheme']:
                return (np.nan, np.nan)
            else:
                return (self.config['single_tok_point'], self.config['single_tok_point']) if morphemes == tokens else (0, 0)
    

    def _load_dataset(self, language_or_filename: str) -> pd.DataFrame:
        """Load dataset for a specific language."""
        if not language_or_filename.endswith('.csv'):
            language = language_or_filename.lower()
            dataset_path = Path(self.config['data_dir']) / f'{language}_data.csv'
        else:
            dataset_path = Path(self.config['data_dir']) / language_or_filename
        
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found for language: {language}") 
        return pd.read_csv(dataset_path)

    def _filter_dataset(self, dataset: pd.DataFrame) -> pd.DataFrame:
        """Apply filtering based on configuration flags."""
        filtered_df = dataset.copy()
        
        # Filter by splits, if the column starts with the split name
        #print(f'Size before split filtering: {len(filtered_df)}')
        if 'data_split' in filtered_df.columns:
            split_dfs = []
            for split in self.config['splits']:
                split_dfs.append(filtered_df[filtered_df['data_split'].str.startswith(split)])
            filtered_df = pd.concat(split_dfs)

        #print(f'Size before unique filtering: {len(filtered_df)}')
        
        # Filter unique only
        if self.config['unique_only'] and 'unique' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['unique'] == 'unique']
        
        #print(f'Size before stem equals lemma filtering: {len(filtered_df)}')
        # Filter stem equals lemma
        if self.config['stem_eq_lemma'] and all(col in filtered_df.columns for col in ['stem', 'lemma']):
            filtered_df = filtered_df[filtered_df['stem'] == filtered_df['lemma']]
        
        #print(f'Size before number filtering: {len(filtered_df)}')
        # Filter out numbers
        if self.config['exclude_numbers'] and 'wordform' in filtered_df.columns:
            filtered_df = filtered_df[~filtered_df['wordform'].astype(str).str.contains(r'\d')]
        
        return filtered_df
    
    
    def get_morphscore(self, dataset: pd.DataFrame, tokenizer, return_df: bool = False) -> tuple:
        """
        Calculate MorphScore for a dataset.
        """
        if not hasattr(tokenizer, 'decode'):
            raise ValueError("Tokenizer must have a 'decode' method")
        
        if not hasattr(tokenizer, 'special_tokens_map'):
            raise ValueError("Tokenizer must have a 'special_tokens_map' attribute")
        
        required_cols = ['stem', 'lemma', 'preceding_part', 'following_part', 'wordform']
        if not all(col in dataset.columns for col in required_cols):
            raise ValueError(f"Dataset must contain columns: {required_cols}")
        
        special_toks = tokenizer.special_tokens_map.values()

        # Score storage
        points_morphscore_recall = []
        points_morphscore_precision = []
        weights = []
        token_char_ratios = []
        matched_subwords = []
        gold_subwords = []
        pred_subwords = []

        def add_nan_values():
            points_morphscore_recall.append(np.nan)
            points_morphscore_precision.append(np.nan)
            matched_subwords.append(np.nan)
            gold_subwords.append(np.nan)
            pred_subwords.append(np.nan)
            weights.append(np.nan)
            token_char_ratios.append(np.nan)

        for idx in range(len(dataset)):
            row = dataset.iloc[idx]
            prefix = row['preceding_part']
            suffix = row['following_part']
            stem = row['stem']
            wordform = row['wordform']
            norm_freq = float(row['word_freq_norm'])

            if not isinstance(wordform, str):
                if pd.isna(wordform):
                    add_nan_values()
                    continue
                wordform = str(wordform).strip()
                if not wordform:
                    add_nan_values()
                    continue

            if not wordform or wordform.isspace():
                add_nan_values()
                continue

            # Assemble gold morphemes
            morphemes = []
            if not pd.isna(prefix):
                morphemes.append(prefix)
            morphemes.append(stem)
            if not isinstance(suffix, float):  # i.e., not NaN
                morphemes.append(suffix)

            # Tokenize
            token_output = tokenizer(wordform)
            token_ids = token_output['input_ids']
            tokens = [tokenizer.decode(token_id) for token_id in token_ids]
            tokens = [t for t in tokens if t not in special_toks]
            if self.config['subword_prefix']:
                tokens = [t.replace(self.config['subword_prefix'], '') for t in tokens]

            # Calculate token_char_ratio
            if len(wordform) > 0:
                token_char_ratios.append(len(tokens) / len(wordform))
            else:
                token_char_ratios.append(np.nan)

            # MorphScore
            point_recall, point_precision = self.morph_eval(morphemes, tokens)

            if self.config['freq_scale'] and not np.isnan(point_recall):
                weights.append(norm_freq)
            elif not np.isnan(point_recall):
                weights.append(1)
            else:
                weights.append(np.nan)  # Will be dropped later

            points_morphscore_recall.append(point_recall)
            points_morphscore_precision.append(point_precision)

            # Traditional metrics
            n_matched = len(set(tokens) & set(morphemes))
            n_gold = len(morphemes)
            n_pred = len(tokens)
            matched_subwords.append(n_matched)
            gold_subwords.append(n_gold)
            pred_subwords.append(n_pred)

        dataset['morphscore_recall'] = points_morphscore_recall
        dataset['morphscore_precision'] = points_morphscore_precision
        dataset['token_char_ratio'] = token_char_ratios
        dataset['matched_subwords'] = matched_subwords
        dataset['gold_subwords'] = gold_subwords
        dataset['pred_subwords'] = pred_subwords

        # Drop NaNs for final scoring
        new_dataset = dataset.dropna(subset=[
            'morphscore_recall', 'morphscore_precision',
            'token_char_ratio', 'matched_subwords',
            'gold_subwords', 'pred_subwords'
        ])
        valid_weights = [w for w in weights if not np.isnan(w)]
        assert len(new_dataset) == len(valid_weights)

        # Weighted MorphScores
        weighted_recall_points = [p * w for p, w in zip(new_dataset['morphscore_recall'], valid_weights)]
        weighted_precision_points = [p * w for p, w in zip(new_dataset['morphscore_precision'], valid_weights)]

        mean_morphscore_recall = float(np.sum(weighted_recall_points) / np.sum(valid_weights))
        mean_morphscore_precision = float(np.sum(weighted_precision_points) / np.sum(valid_weights))

        # Micro scores
        n_matched = np.sum(new_dataset['matched_subwords'])
        n_gold = np.sum(new_dataset['gold_subwords'])
        n_pred = np.sum(new_dataset['pred_subwords'])
        micro_precision = float(n_matched / n_pred)
        micro_recall = float(n_matched / n_gold)
        if micro_precision + micro_recall == 0:
            micro_f1 = 0.0
        else:
            micro_f1 = float(2 * micro_precision * micro_recall / (micro_precision + micro_recall))

        # Macro scores
        all_precs = [row['matched_subwords'] / row['pred_subwords'] for _, row in new_dataset.iterrows()]
        all_recalls = [row['matched_subwords'] / row['gold_subwords'] for _, row in new_dataset.iterrows()]
        macro_precision = float(np.mean(all_precs))
        macro_recall = float(np.mean(all_recalls))
        if (macro_precision + macro_recall) == 0:
            macro_f1 = 0.0
        else:
            macro_f1 = float(2 * macro_precision * macro_recall / (macro_precision + macro_recall))

        mean_token_char_ratio = np.mean(new_dataset['token_char_ratio']) if len(new_dataset['token_char_ratio']) > 0 else 0.0

        results = {
            'morphscore_recall': mean_morphscore_recall,
            'morphscore_precision': mean_morphscore_precision,
            'morphscore_recall_std': np.std(weighted_recall_points) if len(weighted_recall_points) > 1 else 0.0,
            'morphscore_precision_std': np.std(weighted_precision_points) if len(weighted_precision_points) > 1 else 0.0,
            'mean_token_char_ratio': mean_token_char_ratio,
            'micro_precision': micro_precision,
            'micro_recall': micro_recall,
            'micro_f1': micro_f1,
            'macro_precision': macro_precision,
            'macro_recall': macro_recall,
            'macro_f1': macro_f1,
            'num_samples': len(new_dataset)
        }

        return (results, new_dataset) if return_df else results

        
   
    def eval(self, tokenizer, return_df: bool = False) -> Dict[str, Any]:
        results_per_lang = {'config': self.config.copy()}
        new_dataset = None  # Initialize here

        if self.config['language_subset']:
            languages = self.config['language_subset']
        else:
            languages = os.listdir(self.config['data_dir'])

        for language in languages:
            dataset = self._load_dataset(language)
            filtered_data = self._filter_dataset(dataset)

            if len(filtered_data) == 0:
                results_per_lang[language] = {'num_samples': 0, 'error': 'No samples after filtering'}
                continue

            if return_df:
                results, new_dataset = self.get_morphscore(filtered_data, tokenizer, return_df)
            else:
                results = self.get_morphscore(filtered_data, tokenizer, return_df)

            # Breakdown by split 
            if self.config['by_split'] and 'data_split' in filtered_data.columns:
                results['by_split'] = {}
                for split in filtered_data['data_split'].unique():
                    split_data = filtered_data[filtered_data['data_split'] == split]
                    split_results = self.get_morphscore(split_data, tokenizer, return_df=False)
                    results['by_split'][split] = split_results
            
            # Breakdown by POS 
            if self.config['by_pos'] and 'pos' in filtered_data.columns:
                results['by_pos'] = {}
                for pos in filtered_data['pos'].unique():
                    pos_data = filtered_data[filtered_data['pos'] == pos]
                    pos_results = self.get_morphscore(pos_data, tokenizer, return_df=False)
                    results['by_pos'][pos] = pos_results
        
            results_per_lang[language] = results

        if return_df:
            # Return results and the new_dataset (from last language processed)
            return results_per_lang, new_dataset
        else:
            return results_per_lang

    
    def update_config(self, **kwargs):
        """Update configuration parameters."""
        self.config.update(kwargs)
        self._validate_config()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()


if __name__ == "__main__":
    from transformers import AutoTokenizer
    
    # Example usage
    tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
    
    morph_score = MorphScore(language_subset=['turkish'], # set to run on a subset of languages
                            subword_prefix='##', # set if your tokenizer uses a prefix for some subwords
                            by_pos=True, 
                            freq_scale=False)
    results, df = morph_score.eval(tokenizer, return_df=True)
    print(results)