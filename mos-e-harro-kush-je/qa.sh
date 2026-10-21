#!/bin/bash
# Technical QA of a render: stream format, frame count, decode errors, unintended black or frozen frames, loudness,
# and a contact sheet (2 frames/s). Usage: bash qa.sh <video.mp4> [sheet.jpg]
set -euo pipefail
V="$1"; SHEET="${2:-${V%.mp4}-sheet.jpg}"
echo "== streams"
ffprobe -v error -show_entries stream=codec_name,profile,width,height,pix_fmt,r_frame_rate,avg_frame_rate,sample_rate,channels,bit_rate:format=duration,bit_rate -of compact "$V"
echo "== frames"
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nw=1 "$V"
echo "== moov atom position (faststart: moov before mdat)"
python3 - "$V" <<'EOF'
import struct, sys
f = open(sys.argv[1], "rb"); order = []
while True:
    h = f.read(8)
    if len(h) < 8: break
    size, kind = struct.unpack(">I4s", h)
    if size == 1: size = struct.unpack(">Q", f.read(8))[0]; f.seek(size - 16, 1)
    else: f.seek(size - 8, 1)
    order.append(kind.decode())
print(" ".join(order))
EOF
echo "== decode errors (empty = none)"
ffmpeg -v error -i "$V" -f null - 2>&1 | head -5
echo "== black stretches >= 0.1 s (pixel <= 0.06, picture >= 98 %)"
ffmpeg -nostats -i "$V" -vf "blackdetect=d=0.1:pic_th=0.98:pix_th=0.06" -an -f null - 2>&1 | grep -o "black_start.*" || echo "none"
echo "== frozen stretches >= 0.5 s"
ffmpeg -nostats -i "$V" -vf "freezedetect=n=0.002:d=0.5" -an -f null - 2>&1 | grep -o "freeze_[a-z]*: [0-9.]*" || echo "none"
echo "== loudness"
ffmpeg -nostats -i "$V" -af loudnorm=print_format=summary -f null - 2>&1 | grep -E "Input (Integrated|True Peak|LRA)"
ffmpeg -v error -y -i "$V" -vf "fps=2,scale=216:-1,tile=10x6" -frames:v 1 "$SHEET"
echo "== contact sheet: $SHEET"
