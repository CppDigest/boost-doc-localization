# OpenRouter Translation Pipeline

A Python-based translation tool that uses OpenRouter API to translate English markdown documentation to Chinese using various AI models.

## Features

- 🌐 **Multi-Model Support**: Works with any OpenRouter-compatible AI model
- 🔄 **Automatic Retry Logic**: Handles 429 rate limit errors with exponential backoff
- 📝 **Markdown Preservation**: Maintains formatting, code blocks, and structure
- 🏷️ **Smart Naming**: Auto-generates output filenames with model information
- ⚡ **Chunk Processing**: Handles large documents by splitting into manageable chunks
- 🛡️ **Error Resilience**: Graceful fallback for failed translations

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd OpenRouterTranslationPipline
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Set your OpenRouter API key as an environment variable:

```bash
# Windows
set OPENROUTER_API_KEY=your_api_key_here

# Linux/Mac
export OPENROUTER_API_KEY=your_api_key_here
```

### API Key Setup

1. Get your API key from [OpenRouter](https://openrouter.ai/)
2. Set it as an environment variable or pass it via command line

## Usage

### Basic Usage

```bash
python OpenRouter_translator.py <input_file> -m <model_name>
```

### Examples

```bash
# Translate with DeepSeek Chat v3.1
python OpenRouter_translator.py document.md -m "deepseek/deepseek-chat-v3.1:free"

# Translate with DeepSeek R1
python OpenRouter_translator.py document.md -m "deepseek/deepseek-r1-0528:free"

# Using API key from command line
python OpenRouter_translator.py document.md -m "deepseek/deepseek-chat-v3.1:free" -k "your_api_key"
```

### Command Line Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `input_file` | Path to the markdown file to translate | ✅ Yes |
| `-m, --model` | AI model name (e.g., "deepseek/deepseek-chat-v3.1:free") | ✅ Yes |
| `-k, --api-key` | OpenRouter API key (optional if set as environment variable) | ❌ No |

## Output Naming Convention

The tool automatically generates output filenames using the format:
```
@originalname_zh_@modelname.md
```

**Examples:**
- Input: `document.md` → Output: `document_zh_deepseek-chat-v3.1.md`
- Input: `guide.md` → Output: `guide_zh_deepseek-r1-0528.md`

## Supported Models

The tool works with any OpenRouter-compatible model. Popular options include:

- `deepseek/deepseek-chat-v3.1:free`
- `deepseek/deepseek-r1-0528:free`
- `meta-llama/llama-3.1-8b-instruct:free`
- `google/gemini-flash-1.5:free`

## Rate Limiting & Error Handling

### Automatic Retry Logic

The tool includes intelligent retry mechanisms:

- **429 Rate Limit Errors**: Automatically retries with exponential backoff
- **Exponential Backoff**: Delay doubles for each consecutive 429 error
- **Maximum Retries**: Up to 10 retry attempts per chunk
- **Graceful Fallback**: Uses original text if all retries fail

### Backoff Schedule

| Consecutive 429 Errors | Delay Time |
|------------------------|------------|
| 1st error | 1.0 second |
| 2nd error | 2.0 seconds |
| 3rd error | 4.0 seconds |
| 4th error | 8.0 seconds |
| 5th error | 16.0 seconds |
| 6th+ errors | 32.0+ seconds |

## Translation Quality

The tool is specifically optimized for technical documentation translation:

- ✅ **Preserves Markdown formatting**
- ✅ **Maintains code blocks and syntax**
- ✅ **Keeps links and images intact**
- ✅ **Uses accurate technical terminology**
- ✅ **Maintains document structure**
- ✅ **Preserves tables and lists**

## Development

### Project Structure

```
OpenRouterTranslationPipline/
├── OpenRouter_translator.py    # Main translation script
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── .vscode/
│   └── launch.json            # VS Code debug configuration
└── venv/                      # Virtual environment
```

### VS Code Debugging

The project includes VS Code launch configurations for easy debugging:

1. Open the project in VS Code
2. Go to Run and Debug (Ctrl+Shift+D)
3. Select "Python Debugger: OpenRouter Translator"
4. Set breakpoints and debug

### Adding New Features

To extend the tool:

1. **New Models**: Add model-specific configurations in the `__init__` method
2. **Custom Prompts**: Modify the `system_prompt` in `translate_text` method
3. **Output Formats**: Extend the `translate_markdown_file` method
4. **Error Handling**: Add new exception types in the retry logic

## Troubleshooting

### Common Issues

**1. API Key Not Found**
```
ValueError: OpenRouter API key is required
```
**Solution**: Set the `OPENROUTER_API_KEY` environment variable

**2. Model Not Found**
```
ValueError: Model name is required
```
**Solution**: Provide a valid model name with `-m` parameter

**3. Rate Limit Errors**
```
Error code: 429 - Provider returned error
```
**Solution**: The tool automatically handles this with retry logic

**4. File Not Found**
```
FileNotFoundError: [Errno 2] No such file or directory
```
**Solution**: Check the input file path is correct

### Performance Tips

- **Use faster models** for quick translations
- **Split large documents** manually if needed
- **Monitor rate limits** and adjust delays if necessary
- **Use paid models** for higher rate limits

## License

This project is part of the Boost Documentation Localization effort.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the OpenRouter documentation
3. Open an issue in the repository
4. Contact the maintainers

---

**Happy Translating! 🌐📚**

