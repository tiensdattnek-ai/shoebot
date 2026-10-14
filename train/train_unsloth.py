#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
train_unsloth.py – Fine-tune NHANH (nhanh hơn ~2x, tốn ít VRAM hơn ~50%) bằng Unsloth.
Dùng khi chạy trên Google Colab / Kaggle / máy có GPU.

Cài trước:
    pip install unsloth

Chạy:
    python train/train_unsloth.py --model unsloth/Qwen2.5-3B-Instruct \
        --data_dir dataset --output_dir out/shoebot-unsloth --epochs 3

Sau khi train, script sẽ (tuỳ chọn):
    • Lưu LoRA adapter           → out/shoebot-unsloth/final
    • Xuất GGUF để chạy Ollama   → out/shoebot-unsloth/gguf/  (nếu cài llama.cpp/quantize)
"""

import argparse
import json
import os
import sys

# ============================================================ THAM SỐ
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="unsloth/Qwen2.5-3B-Instruct")
    p.add_argument("--data_dir", default="dataset")
    p.add_argument("--output_dir", default="out/shoebot-unsloth")
    p.add_argument("--epochs", type=float, default=3)
    p.add_argument("--max_steps", type=int, default=-1)
    p.add_argument("--batch_size", type=int, default=2)
    p.add_argument("--grad_accum", type=int, default=4)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--max_len", type=int, default=1024)
    p.add_argument("--lora_r", type=int, default=16)
    p.add_argument("--export_gguf", action="store_true", help="Xuất GGUF q4_k_m sau khi train")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def main():
    args = parse_args()
    try:
        from unsloth import FastLanguageModel
        from unsloth.chat_templates import get_chat_template
    except ImportError:
        sys.exit("Chưa cài unsloth. Chạy: pip install unsloth  (nên làm trên Colab/máy có GPU)")
    from datasets import load_dataset
    from trl import SFTTrainer, SFTConfig

    print("=" * 70)
    print("SHOEBOT – FINE-TUNE NHANH VỚI UNSLOTH")
    print("=" * 70)

    # ---------- model + LoRA
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model, max_seq_length=args.max_len, load_in_4bit=True,
        dtype=None,  # tự chọn float16/bfloat16
    )
    tokenizer = get_chat_template(tokenizer, chat_template="qwen-2.5" if "qwen" in args.model.lower() else "llama-3")
    model = FastLanguageModel.get_peft_model(
        model, r=args.lora_r, lora_alpha=args.lora_r * 2, lora_dropout=0.0, bias="none",
        use_gradient_checkpointing="unsloth", random_state=args.seed,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )

    # ---------- dữ liệu (chat template dạng text + EOS)
    train_file = os.path.join(args.data_dir, "train.jsonl")
    if not os.path.exists(train_file):
        sys.exit(f"Không thấy {train_file}. Chạy: python data/build_dataset.py --out {args.data_dir}")

    ds = load_dataset("json", data_files=train_file, split="train")
    EOS = tokenizer.eos_token

    def fmt(ex):
        text = tokenizer.apply_chat_template(ex["messages"], tokenize=False, add_generation_prompt=False)
        return {"text": text + EOS}

    ds = ds.map(fmt, remove_columns=ds.column_names)
    print(f"Dữ liệu: {len(ds)} mẫu | ví dụ cuối:\n…{ds[0]['text'][-260:]}\n")

    # ---------- train
    trainer = SFTTrainer(
        model=model, tokenizer=tokenizer, train_dataset=ds,
        args=SFTConfig(
            dataset_text_field="text", max_seq_length=args.max_len,
            output_dir=args.output_dir, num_train_epochs=args.epochs, max_steps=args.max_steps,
            per_device_train_batch_size=args.batch_size, gradient_accumulation_steps=args.grad_accum,
            learning_rate=args.lr, lr_scheduler_type="cosine", warmup_ratio=0.03,
            logging_steps=10, save_strategy="epoch", save_total_limit=2,
            optim="adamw_8bit", weight_decay=0.01, fp16=True, report_to="none", seed=args.seed,
        ),
    )
    trainer.train()

    out_final = os.path.join(args.output_dir, "final")
    model.save_pretrained(out_final)
    tokenizer.save_pretrained(out_final)
    print(f"✓ Adapter lưu tại: {out_final}")

    # ---------- thử chat ngay
    FastLanguageModel.for_inference(model)
    msgs = [{"role": "system", "content": "Bạn là trợ lý bán hàng giày tại Việt Nam, xưng em, gọi khách là anh/chị."},
            {"role": "user", "content": "Chân em 25.5cm, chân hơi bè, đi Samba size gì ạ?"}]
    inputs = tokenizer.apply_chat_template(msgs, tokenize=True, add_generation_prompt=True, return_tensors="pt").to("cuda")
    out = model.generate(input_ids=inputs, max_new_tokens=200, do_sample=False)
    print("\n--- Trả lời thử ---")
    print(tokenizer.decode(out[0][inputs.shape[-1]:], skip_special_tokens=True))

    # ---------- xuất GGUF (tuỳ chọn)
    if args.export_gguf:
        gguf_dir = os.path.join(args.output_dir, "gguf")
        os.makedirs(gguf_dir, exist_ok=True)
        try:
            model.save_pretrained_gguf(gguf_dir, tokenizer, quantization_method="q4_k_m")
            print(f"✓ GGUF q4_k_m: {gguf_dir}")
            print("  Chạy với Ollama:\n"
                  f"    echo 'FROM {gguf_dir}/model-q4_k_m.gguf\\nTEMPLATE \"\"\"{{{{ .Prompt }}}} \"\"\"' > Modelfile\n"
                  "    ollama create shoebot -f Modelfile && ollama run shoebot")
        except Exception as e:
            print("[!] Không xuất được GGUF tự động:", e)
            print("    Cách thủ công: clone llama.cpp → python convert_hf_to_gguf.py <model> --outtype q4_k_m")

    with open(os.path.join(args.output_dir, "train_log.json"), "w", encoding="utf-8") as f:
        json.dump({"model": args.model, "history": trainer.state.log_history,
                   "n_train": len(ds), "epochs": args.epochs}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
