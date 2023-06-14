import argparse
from datetime import datetime
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from typing import Optional

import spacy
from sutime import SUTime
from nltk.tokenize import sent_tokenize

from src.util import config


def parse_args():
    parser = argparse.ArgumentParser(description='Extract diagnosis time from self-report text')
    
    parser.add_argument(
        '--input_file', type=str, default='data/example_data.json', help='Input file path'
    )
    parser.add_argument(
        '--output_file', type=str, default='output/example_diagnosis_time.json', help='Output file path'
    )
    parser.add_argument(
        '--method', type=str, default='parsing', help='Method to extract diagnosis time'
    )
    
    args = parser.parse_args()
    return args


def get_diagnosis_time(datafile: str, outputfile: str, method: str='parsing'):
    """
    Get diagnosis time and corresponding text expression from diagnosed user data.
    Assume input is a pair of self-report text and created_utc of the report.
    
    method:
        'parsing' (default): use dependency parsing to extract time
        'char_dist': use character distance to extract time
    """
    assert method in ['parsing', 'char_dist']
    with open(config.DIAGPATTERNS_POS, 'r') as fp:
        pattern_pos = fp.read().splitlines()
    with open(config.DEPRESSION_WORDS, 'r') as fp:
        depression_words = fp.read().splitlines()
    sutime = SUTime()
    nlp = spacy.load("en_core_web_sm")
    
    with open(datafile, 'r') as fp:
        data = json.load(fp)
    
    results = []
    for each in data:
        tmp = None
        sent, pat_idx, pat_len = is_diagnosis_text(each['text'], pattern_pos,
            depression_words)
        if sent is not None:
            # find diagnosis expression
            tmp = {'sentence': sent, 'self_report_utc': each['created_utc']}
            extract = get_time_phrase(sent, pat_idx, pat_len, sutime, nlp,
                method=method, created_utc=each['created_utc'])
            if extract is not None:
                tmp['diagnosis_time_value'] = extract['value']
                tmp['diagnosis_time_text'] = extract['text']
            else:
                tmp = None
        results.append(tmp)
    
    # write to file
    with open(outputfile, 'w') as fp:
        json.dump(results, fp)


def get_time_phrase(text: str, pat_idx: int, pat_len: int, sutime,
        nlp, method: str='char_dist', created_utc: Optional[float]=None) -> str:
    """Get diagnosis time from text"""
    created_utc_str = datetime.fromtimestamp(created_utc).strftime("%Y-%m-%d") if \
        created_utc is not None else None
    # extract time phrase
    retrieved_times = sutime.parse(text, reference_date=created_utc_str)
    retrieved_times = [i for i in retrieved_times if i['type'] != 'SET']
    if len(retrieved_times) == 0:
        return None
    pat_end = pat_idx + pat_len
    # calculate char distance
    for ind, each in enumerate(retrieved_times):
        retrieved_times[ind]['char_dist'] = max(pat_idx - each['end'], each['start'] - pat_end)
    if method == 'parsing':
        doc = nlp(text)
        pat_tokens = {i for i in doc if i.idx >= pat_idx and i.idx < pat_end}
        # find head token of the pattern
        counts = {i: 0 for i in pat_tokens}
        for each in pat_tokens:
            for anc in each.ancestors:
                if anc in pat_tokens:
                    counts[anc] += 1
        pat_head = sorted(pat_tokens, key=lambda x: counts[x], reverse=True)[0]
        assert len(set(pat_head.ancestors).intersection(pat_tokens)) == 0
        results = get_time_phrase_from_head(pat_head, retrieved_times)
        if len(results) == 0:
            if pat_head.dep_ not in {'ccomp', 'parataxis', 'conj', 'advcl'}:
                results = get_time_phrase_from_head(pat_head.head, retrieved_times)
    else:
        results = retrieved_times
    if len(results) == 0:
        return None
    # sort by char_dist
    results = sorted(results, key=lambda x: x['char_dist'])
    return results[0]


def get_time_phrase_from_head(head, options):
    exclude_dep = {'conj', 'parataxis', 'advcl'}
    children = [i for i in head.children if i.dep_ not in exclude_dep]
    subtree = {i.idx for child in children for i in child.subtree}
    results = [i for i in options if i['start'] in subtree]
    return results


def is_diagnosis_text(text, pattern_pos, depression_words):
    """
    Given text, determine if it's self-report diagnosis text.
    Return self-report sentence, index, pattern length if yes.
    """
    sentences = sent_tokenize(text)
    sentences_l = [i.lower() for i in sentences]
    for sent_id, sent in enumerate(sentences):
        for pat in pattern_pos:
            start = sentences_l[sent_id].find(pat)
            if start >= 0:
                # Additionally check if there is depression words in the sentence
                text_span = sentences_l[sent_id][max(0, start - 50): start + len(pat) + 100]
                if any([i in text_span for i in depression_words]):
                    # find the diagnose sentence
                    return sent, start, len(pat)
    
    return None, None, None


if __name__ == "__main__":
    args = parse_args()
    get_diagnosis_time(args.input_file, args.output_file, args.method)
