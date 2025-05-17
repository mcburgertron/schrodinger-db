import sys
from openai import OpenAI


def main() -> None:
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("qwen0.6b> ")
    response = client.chat.completions.create(
        model="qwen3:0.6b",
        messages=[{"role": "user", "content": prompt}],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
