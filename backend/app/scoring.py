import pandas as pd
import numpy as np
import re
from typing import List,Dict,Any,Optional
from sentence_transformers import SentenceTransformer,util

#intialize model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = None

def get_model():
    global _model 
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME) 
    return _model

def load_rubric(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
    else :
        df = pd.read_excel(path)
    #normalize
    df['keywords'] = df.get('keywords','').fillna('').astype(str).apply(
        lambda s: [k.strip().lower() for k in re.split(r',|;',s) if k.strip()]
    )
    df['min_word'] = pd.to_numeric(df['min_word'] if 'min_word' in df else 0, errors='coerce')
    df['min_word'] = df['min_word'].fillna(0).astype(int)

    df['max_word'] = pd.to_numeric(df['max_word'] if 'max_word' in df else 9999, errors='coerce')
    df['max_word'] = df['max_word'].fillna(9999).astype(int)

    df['weight'] = pd.to_numeric(df.get('weight'),errors='coerce').fillna(1.0)
    
    model = get_model()
    descs = df['description'].fillna('').astype(str).tolist()
    df['desc_emb'] = list(model.encode(descs,convert_to_numpy=True,show_progress_bar=False))
    return df

_word_regex = re.compile(r"\b\w+\b",re.UNICODE)

def tokenize_word(text:str) -> List[str]:
    text = text.lower()
    return _word_regex.findall(text)

def keyword_scrore(transcript:str,keywords: List[str]) -> float:
    if not keywords:
        return 0.0
    words = set(tokenize_word(transcript))
    found = 0
    for kw in keywords:
        if kw in words or kw in transcript.lower():
            found +=1
    return found /len(keywords)

def wordcount_score(words:int ,min_w:int,max_w:int) -> float:
    if min_w <= words <= max_w:
        return 1.0
    if words < min_w:
        if min_w == 0:
            return 1.0
        penalty = (min_w - words)/min_w
        return max(0.0,1.0 - penalty)
    else:
        if max_w ==0:
            return 0.0
        penalty = (words -max_w)/max_w
        return max(0.0,1.0-penalty)
    
def semantic_score(transcript: str,desc_emb:np.ndarray) -> float:
    model = get_model()
    emb = model.encode(transcript,convert_to_numpy=True)
    sim = util.cos_sim(emb,desc_emb).item()
    mapped = (sim +1)/2
    return float(max(0.0,min(1.0,mapped)))

def score_transcript(transcript: str,rubric_df:pd.DataFrame,comp_weights:Optional[Dict[str,float]] = None) -> Dict[str,Any]:
    """comp_weights: dictionary with keys 'kw', 'wc', 'sem' for component weights.""" 
    if comp_weights is None:
      comp_weights = {'kw':0.4,'wc':0.1,'sem':0.5}
    words_count = len(tokenize_word(transcript))
    total_weight = rubric_df['weight'].sum()
    results = []
    overall_score = 0.0
    
    for ind,row in rubric_df.iterrows():
        kw = keyword_scrore(transcript,row['keywords'])
        wc = wordcount_score(words_count,int(row['min_words']),int(row['max_words']))
        sem = semantic_score(transcript,row['desc_emb'])
        score_raw = comp_weights['kw'] * kw + comp_weights['wc'] * wc + comp_weights['sem'] *sem
        criterion_score = float(score_raw*100.0)
        contrib = score_raw*(float(row['weight'])/float(total_weight)*100.0)
        overall_score += contrib
        
        found_keywords = []
        trans_lower = transcript.lower()
        for k in row['keywords']:
            if not k:
                continue
            if k in tokenize_word(trans_lower) or k in trans_lower:
                found_keywords.append(k)
        feedback =[]
        if sem >= 0.7:
            feedback.append("Good semantic match.")
        elif sem >= 0.4:
            feedback.append("Partial semantic match,could be clearer.")
        else:
            feedback.append("Low semantic match to rubric.")
        
        if kw >=0.75:
            feedback.append("Most keywords present.")
        elif kw >0:
            feedback.append("Some keywords presents.")
        else:
            feedback.append("No rubric keyword found; consider adding them.")
            
        if wc < 0.5:
            feedback.append(f"Word count {words_count} Outside suggested range [{row['min_words']},{row['max_words']}].")
            
        results.append({
             "criterion_id": row.get('criterion_id', f"C{ind+1}"),
            "criterion_name": row.get('criterion_name', row.get('description', '') ) ,
            "score": round(criterion_score, 2),
            "weight": float(row['weight']),
            "keywords_found": found_keywords,
            "keyword_score": round(kw, 3),
            "word_count_score": round(wc, 3),
            "semantic_score": round(sem, 3),
            "words": words_count,
            "feedback": " ".join(feedback)
        })
        
    overall_score = max(0.0,min(100.0,overall_score))
    return{
        "overall_score":round(overall_score,2),
        "words":words_count,
        "criteria":results
    }
        