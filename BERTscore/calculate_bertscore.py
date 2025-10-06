#!/usr/bin/env python3
"""
Calculate BERTScore for cross-lingual evaluation:
English reference: Boost.Unordered_sample.md
Chinese candidates: All 4 candidates from candidates.txt
"""

import os
import warnings
from bert_score import score
import time

# Suppress HuggingFace warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore", message="Xet Storage is enabled")
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")

def read_file_content(filename):
    """Read file content with proper encoding"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def evaluate_candidate(reference, candidate_text, candidate_name, model_type, model_name, rescale=False):
    """Evaluate a single candidate against reference"""
    try:
        print(f"  Evaluating with {model_name}...")
        start_time = time.time()
        
        if rescale:
            P, R, F1 = score(
                [candidate_text],
                [reference],
                model_type=model_type,
                lang="zh",  # Specify language for rescaling
                rescale_with_baseline=True,
                verbose=False
            )
        else:
            P, R, F1 = score(
                [candidate_text],
                [reference],
                model_type=model_type,
                verbose=False
            )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return {
            'precision': P.item(),
            'recall': R.item(),
            'f1': F1.item(),
            'time': processing_time
        }
    except Exception as e:
        print(f"    Error with {model_name}: {e}")
        return None

def main():
    print("=== BERTScore Cross-lingual Evaluation for Multiple Candidates ===")
    print()
    
    # Read reference file
    print("Reading reference file...")
    reference = read_file_content("Boost.Unordered_sample.md")
    if reference is None:
        print("Failed to read reference file. Exiting.")
        return
    
    print(f"Reference: Boost.Unordered_sample.md ({len(reference)} characters)")
    print()
    
    # Read candidate files
    print("Reading candidate files...")
    candidates = []
    
    with open("candidates.txt", "r", encoding="utf-8") as f:
        candidate_files = [line.strip() for line in f if line.strip()]
    
    for candidate_file in candidate_files:
        content = read_file_content(candidate_file)
        if content is not None:
            candidates.append({
                'name': candidate_file,
                'content': content,
                'length': len(content)
            })
            print(f"  ✓ {candidate_file} ({len(content)} characters)")
        else:
            print(f"  ✗ Failed to read {candidate_file}")
    
    print(f"\nTotal candidates loaded: {len(candidates)}")
    print()
    
    # Define evaluation models
    models = [
        {
            'type': 'bert-base-multilingual-cased',
            'name': 'Multilingual BERT (Cross-lingual)',
            'rescale': False
        },
        {
            'type': 'xlm-roberta-base',
            'name': 'XLM-RoBERTa (Best Cross-lingual)',
            'rescale': False
        },
        {
            'type': 'bert-base-multilingual-cased',
            'name': 'Multilingual BERT (Rescaled)',
            'rescale': True
        }
    ]
    
    # Evaluate each candidate
    results = {}
    
    for i, candidate in enumerate(candidates, 1):
        print(f"=== Candidate {i}: {candidate['name']} ===")
        print(f"Length: {candidate['length']} characters")
        print()
        
        candidate_results = {}
        
        for model in models:
            print(f"Model: {model['name']}")
            result = evaluate_candidate(
                reference,
                candidate['content'],
                candidate['name'],
                model['type'],
                model['name'],
                model['rescale']
            )
            
            if result:
                candidate_results[model['name']] = result
                print(f"  Precision: {result['precision']:.4f}")
                print(f"  Recall: {result['recall']:.4f}")
                print(f"  F1: {result['f1']:.4f}")
                print(f"  Time: {result['time']:.2f}s")
            else:
                print(f"  Failed to evaluate with {model['name']}")
            
            print()
        
        results[candidate['name']] = candidate_results
        print("-" * 80)
        print()
    
    # Summary comparison
    print("=== SUMMARY COMPARISON ===")
    print()
    
    # Create comparison table
    print("F1 Scores Comparison:")
    print("=" * 120)
    print(f"{'Candidate':<50} {'Multilingual BERT':<20} {'XLM-RoBERTa':<15} {'Rescaled BERT':<15}")
    print("=" * 120)
    
    for candidate_name, candidate_results in results.items():
        short_name = candidate_name.replace('Boost.Unordered_sample_zh_', '').replace('.md', '')
        multilingual_f1 = candidate_results.get('Multilingual BERT (Cross-lingual)', {}).get('f1', 0)
        xlm_f1 = candidate_results.get('XLM-RoBERTa (Best Cross-lingual)', {}).get('f1', 0)
        rescaled_f1 = candidate_results.get('Multilingual BERT (Rescaled)', {}).get('f1', 0)
        
        print(f"{short_name:<50} {multilingual_f1:<20.4f} {xlm_f1:<15.4f} {rescaled_f1:<15.4f}")
    
    print("=" * 120)
    print()
    
    # Find best performers
    print("Best Performers:")
    print("-" * 50)
    
    # Best XLM-RoBERTa
    best_xlm = max(results.items(), 
                   key=lambda x: x[1].get('XLM-RoBERTa (Best Cross-lingual)', {}).get('f1', 0))
    print(f"Best XLM-RoBERTa F1: {best_xlm[0]} ({best_xlm[1].get('XLM-RoBERTa (Best Cross-lingual)', {}).get('f1', 0):.4f})")
    
    # Best Multilingual BERT
    best_multilingual = max(results.items(), 
                           key=lambda x: x[1].get('Multilingual BERT (Cross-lingual)', {}).get('f1', 0))
    print(f"Best Multilingual BERT F1: {best_multilingual[0]} ({best_multilingual[1].get('Multilingual BERT (Cross-lingual)', {}).get('f1', 0):.4f})")
    
    # Best Rescaled BERT
    best_rescaled = max(results.items(), 
                       key=lambda x: x[1].get('Multilingual BERT (Rescaled)', {}).get('f1', 0))
    print(f"Best Rescaled BERT F1: {best_rescaled[0]} ({best_rescaled[1].get('Multilingual BERT (Rescaled)', {}).get('f1', 0):.4f})")
    
    print()
    print("Evaluation completed!")

if __name__ == "__main__":
    main()
