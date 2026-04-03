#!/usr/bin/env python3
"""Generate images using Gemini native image generation (Nano Banana).

Docs: https://ai.google.dev/gemini-api/docs/image-generation
"""

import argparse
import os
import sys


VALID_RATIOS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3",
    "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]


def main():
    parser = argparse.ArgumentParser(description="Generate images with Gemini (Nano Banana)")
    parser.add_argument("--prompt", required=True, help="Text description for the image")
    parser.add_argument("--aspect-ratio", default="1:1", choices=VALID_RATIOS,
                        help="Aspect ratio (default: 1:1)")
    parser.add_argument("--size", default="1K", choices=["512px", "1K", "2K", "4K"],
                        help="Image size (default: 1K)")
    parser.add_argument("--model", default="gemini-3.1-flash-image-preview",
                        help="Model ID (default: gemini-3.1-flash-image-preview)")
    parser.add_argument("--output", default="./output.png", help="Output file path")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable")
        print("Get one at: https://aistudio.google.com/apikey")
        sys.exit(1)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Installing google-genai...")
        os.system(f"{sys.executable} -m pip install -q google-genai Pillow")
        from google import genai
        from google.genai import types

    client = genai.Client(api_key=api_key)

    print(f"Model: {args.model}")
    print(f"Prompt: {args.prompt}")
    print(f"Aspect: {args.aspect_ratio} | Size: {args.size}")
    print("Generating image...")

    response = client.models.generate_content(
        model=args.model,
        contents=args.prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=args.aspect_ratio,
                image_size=args.size,
            ),
        ),
    )

    # Extract image from response
    saved = False
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            output_path = os.path.abspath(args.output)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(part.inline_data.data)
            print(f"Image saved to: {output_path}")
            saved = True
            break
        elif hasattr(part, "text") and part.text:
            print(f"Model response: {part.text}")

    if not saved:
        print("ERROR: No image was generated. The prompt may have been filtered.")
        sys.exit(1)


if __name__ == "__main__":
    main()
