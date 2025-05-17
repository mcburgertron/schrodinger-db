import argparse
from openai import OpenAI


def main() -> None:
    parser = argparse.ArgumentParser(description="Query a local Qwen model")
    parser.add_argument(
        "-m",
        "--model",
        default="qwen3:0.6b",
        help="Ollama model identifier",
    )
    parser.add_argument("prompt", nargs="*", help="Prompt text")
    args = parser.parse_args()

    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    prompt = " ".join(args.prompt) if args.prompt else input(f"{args.model}> ")
    response = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": prompt}],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
