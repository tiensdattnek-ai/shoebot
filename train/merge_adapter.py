#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_adapter.py – Gộp LoRA adapter vào model gốc để có 1 model "sạch" (chạy nhanh hơn khi suy luận,
không cần cài peft, dễ mang đi deploy/quantize).

    python train/merge_adapter.py \
        --model Qwen/Qwen2.5-3B-Instruct \
        --adapter out/shoebot-lora/final \
        --out out/shoebot-merged

Sau đó:
    python app/chat_cli.py --model out/shoebot-merged
"""

import argparse
import os
import sys

import torch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="Model gốc (HF id hoặc đường dẫn)")
    ap.add_argument("--adapter", required=True, help="Thư mục LoRA adapter (vd out/shoebot-lora/final)")
    ap.add_argument("--out", required=True, help="Thư mục lưu model đã gộp")
    ap.add_argument("--dtype", default="float16", choices=["float16", "bfloat16", "float32"])
    args = ap.parse_args()

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    dtype = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}[args.dtype]
    print(f"→ Nạp base: {args.model} ({args.dtype})")
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype, low_cpu_mem_usage=True,
                                                 trust_remote_code=True)
    print(f"→ Gắn adapter: {args.adapter}")
    model = PeftModel.from_pretrained(model, args.adapter)
    print("→ Gộp trọng số…")
    model = model.merge_and_unload()

    os.makedirs(args.out, exist_ok=True)
    model.save_pretrained(args.out, safe_serialization=True)
    AutoTokenizer.from_pretrained(args.model).save_pretrained(args.out)
    print(f"✓ Đã lưu model gộp tại: {args.out}")
    print("\nGợi ý bước tiếp theo:")
    print(f"  • Chat thử : python app/chat_cli.py --model {args.out}")
    print(f"  • Web UI   : python app/app_gradio.py --model {args.out}")
    print("  • Xuất GGUF (để chạy bằng llama.cpp/Ollama): dùng llama.cpp convert_hf_to_gguf.py "
          f"--outfile shoebot-Q4_K_M.gguf --outtype q4_k_m {args.out}")


if __name__ == "__main__":
    main()
