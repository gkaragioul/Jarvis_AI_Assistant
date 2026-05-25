from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib import request


def post_json(url: str, payload: dict, timeout: int) -> bytes:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as res:
        if res.status != 200:
            raise RuntimeError(f"TTS failed: HTTP {res.status}")
        return res.read()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Derek teacher audio for fast-runtime training.")
    parser.add_argument("--root", default=r"X:\Jarvis\fast-derek")
    parser.add_argument("--tts-url", default="http://127.0.0.1:11550/synthesize")
    parser.add_argument("--prompts", default=r"X:\Jarvis\fast-derek\prompts\conversation_seed.txt")
    parser.add_argument("--limit", type=int, default=0, help="0 means all prompts")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    root = Path(args.root)
    prompts_path = Path(args.prompts)
    wav_dir = root / "dataset" / "wavs"
    wav_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = root / "dataset" / "metadata.csv"

    prompts = [line.strip() for line in prompts_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.limit > 0:
        prompts = prompts[: args.limit]

    rows: list[tuple[str, str]] = []
    for index, text in enumerate(prompts, start=1):
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
        name = f"derek_{index:04d}_{digest}.wav"
        out = wav_dir / name
        if not out.exists():
            audio = post_json(
                args.tts_url,
                {
                    "text": text,
                    "voice_id": "jarvis_online_derek",
                    "fx": "presence",
                    "speed": 1.0,
                },
                args.timeout,
            )
            out.write_bytes(audio)
        rows.append((str(Path("wavs") / name).replace("\\", "/"), text))
        print(f"{index}/{len(prompts)} {name}: {text}")

    with metadata_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerows(rows)

    print(f"metadata={metadata_path}")


if __name__ == "__main__":
    main()
