"""
Video / Audio Interview Transcriber (faster-whisper)
----------------------------------------------------
Batch-transcribes every media file in ../data/ to a plain-text transcript
in ../output/ with per-segment timestamps formatted as [HH:MM:SS].

Run from this directory:
    cd whisper
    pip install -r requirements.txt
    python transcribe.py
"""

from pathlib import Path

from faster_whisper import WhisperModel
from tqdm import tqdm

# ─────────────────────────────────────────────
# CONFIGURE THESE BEFORE RUNNING
# ─────────────────────────────────────────────

INPUT_DIR = "../data"            # Directory scanned for media files
OUTPUT_DIR = "../output"         # Directory where .txt transcripts are written
INPUT_EXTENSIONS = (             # Files with these suffixes are processed
    ".mp4", ".mov", ".mkv", ".webm",
    ".m4a", ".mp3", ".wav", ".flac",
)

MODEL_SIZE = "large-v3"          # tiny | base | small | medium | large-v3 | large-v3-turbo
DEVICE = "cpu"                   # "cpu" or "cuda"
COMPUTE_TYPE = "int8"            # int8 for CPU; float16 or int8_float16 for CUDA
LANGUAGE = "en"                  # ISO code, or None to auto-detect per file
BEAM_SIZE = 5                    # Higher = more accurate, slower

VAD_FILTER = True                # Voice-activity-detection: skip silent regions
SKIP_EXISTING = True             # Don't re-transcribe if <name>.txt already exists


def find_inputs(input_dir: Path) -> list[Path]:
    """Return media files in input_dir, sorted by name. Non-recursive."""
    return sorted(
        p for p in input_dir.iterdir()
        if p.is_file()
        and not p.name.startswith(".")
        and p.suffix.lower() in INPUT_EXTENSIONS
    )


def format_timestamp(seconds: float) -> str:
    """Convert seconds (float) to 'HH:MM:SS' (integer floor)."""
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def transcribe_file(model: WhisperModel, input_path: Path, output_path: Path) -> int:
    """Transcribe one file. Returns the number of segments written."""
    segments, info = model.transcribe(
        str(input_path),
        language=LANGUAGE,
        beam_size=BEAM_SIZE,
        vad_filter=VAD_FILTER,
    )

    segment_count = 0
    last_end = 0.0

    with output_path.open("w", encoding="utf-8") as out, tqdm(
        total=round(info.duration, 2),
        unit="sec",
        desc=input_path.name,
        leave=False,
    ) as pbar:
        for seg in segments:
            line = f"[{format_timestamp(seg.start)}] {seg.text.strip()}\n"
            out.write(line)
            out.flush()
            segment_count += 1
            pbar.update(max(0.0, seg.end - last_end))
            last_end = seg.end

    return segment_count


def main() -> None:
    input_dir = Path(INPUT_DIR)
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    inputs = find_inputs(input_dir)
    if not inputs:
        print(f"No media files found in {input_dir.resolve()} "
              f"(extensions: {', '.join(INPUT_EXTENSIONS)})")
        return

    pending: list[tuple[Path, Path]] = []
    for src in inputs:
        dst = output_dir / f"{src.stem}.txt"
        if SKIP_EXISTING and dst.exists():
            print(f"• {src.name} → {dst.name} (skipping, output exists)")
            continue
        pending.append((src, dst))

    if not pending:
        print("Nothing to do — all inputs already transcribed.")
        return

    print(f"Loading model: {MODEL_SIZE} (device={DEVICE}, compute_type={COMPUTE_TYPE})")
    model = WhisperModel(
        MODEL_SIZE,
        device=DEVICE,
        compute_type=COMPUTE_TYPE,
    )

    for src, dst in pending:
        print(f"▶ {src.name}")
        n = transcribe_file(model, src, dst)
        print(f"✓ {src.name} → {dst.name} ({n} segments)")


if __name__ == "__main__":
    main()
