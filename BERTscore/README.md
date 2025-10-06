# BERTScore Cross-lingual Evaluation Project

## Overview

This project demonstrates how to use BERTScore for cross-lingual evaluation, specifically comparing English reference texts with Chinese translation candidates. BERTScore is an automatic evaluation metric that uses contextual embeddings to compute semantic similarity between texts in different languages.

## Features

- **Cross-lingual BERTScore evaluation** using multilingual models
- **Multiple model support**: XLM-RoBERTa, Multilingual BERT, and Rescaled BERT
- **Batch evaluation** of multiple translation candidates
- **Comprehensive comparison reports** with detailed metrics
- **Professional-grade translation quality assessment**

## Requirements

### System Requirements
- Python 3.8 or higher
- CUDA-compatible GPU (recommended for faster processing)
- At least 4GB RAM

### Python Dependencies
```bash
pip install bert-score
pip install torch
pip install transformers
```

## Installation

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install bert-score torch transformers
```

## Project Structure

```
BERTscore/
├── README.md                           # This file
├── calculate_bertscore.py             # Main evaluation script
├── reference.txt                       # Reference file list
├── candidates.txt                      # Candidate file list
├── Boost.Unordered_sample.md          # English reference document
├── Boost.Unordered_sample_zh_DeepL.md # DeepL translation
├── Boost.Unordered_sample_zh_deepseek-chat-v3.1(free).md # DeepSeek Chat v3.1 (Free)
├── Boost.Unordered_sample_zh_deepseek-r1-0528.md # DeepSeek R1-0528
├── Boost.Unordered_sample_zh_deepseek-r1-0528(free).md # DeepSeek R1-0528 (Free)
└── venv/                              # Virtual environment (created after setup)
```

## Usage

### Quick Start

1. **Prepare your files:**
   - Place your English reference document in the project directory
   - Place your Chinese candidate documents in the project directory
   - Update `reference.txt` with your reference filename
   - Update `candidates.txt` with your candidate filenames

2. **Run the evaluation:**
   ```bash
   python calculate_bertscore.py
   ```

3. **View results:**
   - Check the console output for detailed metrics
   - Review the summary comparison table in the output

### File Configuration

#### reference.txt
```
Boost.Unordered_sample.md
```

#### candidates.txt
```
Boost.Unordered_sample_zh_DeepL.md
Boost.Unordered_sample_zh_deepseek-chat-v3.1(free).md
Boost.Unordered_sample_zh_deepseek-r1-0528.md
Boost.Unordered_sample_zh_deepseek-r1-0528(free).md
```

## Evaluation Models

The script uses three different cross-lingual evaluation approaches:

### 1. XLM-RoBERTa (Best Cross-lingual Model)
- **Model**: `xlm-roberta-base`
- **Purpose**: Best overall cross-lingual performance
- **Use case**: Primary evaluation metric

### 2. Multilingual BERT (Cross-lingual Baseline)
- **Model**: `bert-base-multilingual-cased`
- **Purpose**: Standard cross-lingual baseline
- **Use case**: Comparative analysis

### 3. Rescaled Multilingual BERT (Interpretable Range)
- **Model**: `bert-base-multilingual-cased` with rescaling
- **Purpose**: Human-interpretable scores
- **Use case**: Normalized comparison

## Understanding Results

### Metrics Explained

- **Precision**: How well the candidate captures the semantic content of the reference
- **Recall**: How much of the reference's semantic content is preserved in the candidate
- **F1 Score**: Harmonic mean of precision and recall (primary metric)

### Performance Levels

- **🏆 Outstanding**: F1 > 95% (Professional-grade quality)
- **✅ Excellent**: F1 90-95% (High-quality translation)
- **✅ Good**: F1 80-90% (Good translation quality)
- **⚠️ Fair**: F1 70-80% (Acceptable quality)
- **❌ Poor**: F1 < 70% (Needs improvement)

## Example Results

Based on our evaluation of Boost.Unordered documentation:

| Translation Engine | XLM-RoBERTa F1 | Performance Level | Rank |
|-------------------|----------------|-------------------|------|
| **DeepSeek R1-0528 (Free)** | 95.77% | 🏆 Outstanding | 🥇 1st |
| **DeepL** | 95.65% | 🏆 Outstanding | 🥈 2nd |
| **DeepSeek R1-0528** | 94.63% | 🏆 Outstanding | 🥉 3rd |
| **DeepSeek Chat v3.1 (Free)** | 93.08% | ✅ Excellent | 4th |

## Customization

### Adding New Models

To add new evaluation models, modify the `models` list in `calculate_bertscore.py`:

```python
models = [
    {
        'type': 'your-model-name',
        'name': 'Your Model Description',
        'rescale': False  # Set to True for rescaled evaluation
    }
]
```

### Changing Evaluation Parameters

Modify the `score()` function calls in `evaluate_candidate()`:

```python
P, R, F1 = score(
    [candidate_text],
    [reference],
    model_type=model_type,
    lang="zh",  # Language code for rescaling
    rescale_with_baseline=True,  # Enable rescaling
    verbose=False  # Suppress verbose output
)
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'bert_score'**
   ```bash
   pip install bert-score
   ```

2. **UnicodeDecodeError**
   - Ensure all text files are saved with UTF-8 encoding
   - Check file paths for special characters

3. **CUDA out of memory**
   - Use CPU-only mode by setting `device="cpu"` in score function
   - Reduce batch size if processing multiple candidates

4. **Slow processing**
   - Use GPU acceleration if available
   - Consider using smaller models for faster evaluation

### Performance Optimization

- **GPU Acceleration**: Install CUDA-compatible PyTorch
- **Batch Processing**: Process multiple candidates in single run
- **Model Caching**: Models are automatically cached after first download

## Output

The script provides comprehensive console output including:
- Real-time evaluation progress
- Individual candidate results with precision, recall, and F1 scores
- Summary comparison table showing F1 scores for all candidates
- Best performer identification for each model type

## Best Practices

1. **File Preparation**
   - Use UTF-8 encoding for all text files
   - Ensure consistent formatting
   - Remove unnecessary whitespace

2. **Evaluation Strategy**
   - Use XLM-RoBERTa as primary metric
   - Compare across multiple models
   - Consider rescaled scores for interpretability

3. **Result Interpretation**
   - Focus on F1 scores for overall quality
   - Consider precision vs recall trade-offs
   - Look for consistent performance across models

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- **BERTScore**: Original BERTScore implementation
- **Hugging Face**: Model hosting and transformers library
- **Boost C++**: Documentation used for evaluation examples

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review console output for error messages
3. Ensure all dependencies are properly installed
4. Verify file encoding and format

## Version History

- **v1.0**: Initial cross-lingual evaluation implementation
- **v1.1**: Added multi-candidate batch evaluation
- **v1.2**: Enhanced comparison reporting
- **v1.3**: Added comprehensive documentation

---

**Note**: This project is designed for cross-lingual evaluation of technical documentation. For best results, ensure your reference and candidate texts are well-formatted and semantically aligned.
