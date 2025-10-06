#!/usr/bin/env python3
"""
OpenRouter API Translation Script using OpenAI SDK
Translates English markdown documentation to Chinese using various AI models via OpenRouter
"""

import os
import time
from typing import List
from openai import OpenAI

class OpenRouterTranslator:
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the OpenRouter translator using OpenAI SDK
        
        Args:
            api_key: OpenRouter API key. If None, will try to get from environment variable OPENROUTER_API_KEY
            model: Model name to use. Required parameter.
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize OpenAI client with OpenRouter endpoint
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        # Model configuration - required parameter
        if not model:
            raise ValueError("Model name is required. Pass model parameter or set OPENROUTER_MODEL environment variable.")
        self.model = model
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        self.max_retries = 15  # maximum number of retries for 429 errors
        
    def translate_text(self, text: str, context: str = "") -> str:
        """
        Translate text using AI model via OpenRouter API with OpenAI SDK
        
        Args:
            text: Text to translate
            context: Additional context for better translation
            
        Returns:
            Translated text
        """
        # Prepare the prompt for translation
        system_prompt = """你是一个专业的文档翻译专家，专门负责将技术文档从英文翻译成中文。请遵循以下要求：

1. 保持原文的格式和结构，包括markdown语法
2. 保持代码块、链接、图片等元素不变
3. 技术术语要准确翻译，保持专业性
4. 保持原文的语气和风格
5. 对于C++相关的技术内容，使用标准的中文技术术语
6. 保持表格格式和结构
7. 不要添加或删除任何内容，只进行翻译

请将以下英文内容翻译成中文："""

        user_prompt = f"{context}\n\n{text}" if context else text
        
        # Retry logic with exponential backoff for 429 errors
        retry_delay = self.request_delay
        consecutive_429_errors = 0
        
        for attempt in range(self.max_retries + 1):
            try:
                completion = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "https://github.com/boost-doc-localization",
                        "X-Title": "Boost Documentation Translation"
                    },
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0,
                    max_tokens=30000
                )
                
                translated_text = completion.choices[0].message.content
                
                # Reset consecutive 429 error counter on success
                consecutive_429_errors = 0
                
                # Add delay to respect rate limits
                time.sleep(self.request_delay)
                
                return translated_text
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a 429 rate limit error
                if "429" in error_str and "rate" in error_str.lower():
                    consecutive_429_errors += 1
                    
                    if attempt < self.max_retries:
                        # Calculate exponential backoff delay
                        backoff_delay = retry_delay * (2 ** consecutive_429_errors)
                        print(f"Rate limit error (429) - attempt {attempt + 1}/{self.max_retries + 1}. Retrying in {backoff_delay:.1f} seconds...")
                        time.sleep(backoff_delay)
                        continue
                    else:
                        print(f"Max retries ({self.max_retries}) exceeded for 429 errors. Using original text.")
                        return text  # Return original text if all retries fail
                else:
                    # For non-429 errors, raise immediately
                    print(f"API request failed: {e}")
                    raise
    
    def split_content_for_translation(self, content: str, max_chunk_size: int = 3000) -> List[str]:
        """
        Split content into chunks suitable for translation
        
        Args:
            content: Full content to split
            max_chunk_size: Maximum size of each chunk
            
        Returns:
            List of content chunks
        """
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line) + 1  # +1 for newline
            
            # If adding this line would exceed max size, save current chunk
            if current_size + line_size > max_chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        # Add the last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def translate_markdown_file(self, input_file: str) -> str:
        """
        Translate a markdown file from English to Chinese
        
        Args:
            input_file: Path to input markdown file
            
        Returns:
            Path to the translated file
        """
        base_name = os.path.splitext(input_file)[0]
        # Extract model name from the full model string (e.g., "deepseek/deepseek-chat-v3.1:free" -> "deepseek-chat-v3.1")
        model_name = self.model.split('/')[-1].split(':')[0]
        output_file = f"{base_name}_zh_{model_name}.md"
        
        print(f"Reading file: {input_file}")
        print(f"Using model: {self.model}")
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Content length: {len(content)} characters")
        
        # Split content into manageable chunks
        chunks = self.split_content_for_translation(content, 15000)
        print(f"Split into {len(chunks)} chunks for translation")
        
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            print(f"Translating chunk {i+1}/{len(chunks)}...")
            
            # Add context for better translation
            context = "This is a technical documentation about Boost C++ Libraries, specifically about Boost.Unordered hash containers. Please translate maintaining all technical accuracy and formatting."
            
            try:
                translated_chunk = self.translate_text(chunk, context)
                translated_chunks.append(translated_chunk)
                print(f"Chunk {i+1} translated successfully")
                
            except Exception as e:
                print(f"Error translating chunk {i+1}: {e}")
                # Add original chunk if translation fails
                translated_chunks.append(chunk)
        
        # Combine all translated chunks
        translated_content = '\n'.join(translated_chunks)
        
        # Write translated content to file
        print(f"Writing translated content to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        
        print(f"Translation completed! Output saved to: {output_file}")
        return output_file

def main():
    """Main function to run the translation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Translate markdown files using OpenRouter API with OpenAI SDK')
    parser.add_argument('input_file', help='Input markdown file to translate')
    parser.add_argument('-k', '--api-key', help='OpenRouter API key (optional, can use OPENROUTER_API_KEY env var)')
    parser.add_argument('-m', '--model', required=True, help='Model name (required)')
    
    args = parser.parse_args()
    
    try:
        # Initialize translator
        translator = OpenRouterTranslator(api_key=args.api_key, model=args.model)
        
        # Translate the file
        output_file = translator.translate_markdown_file(args.input_file)
        
        print(f"\nTranslation completed successfully!")
        print(f"Input file: {args.input_file}")
        print(f"Output file: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
