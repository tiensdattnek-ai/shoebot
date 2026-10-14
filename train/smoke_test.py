#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
smoke_test.py – Chạy thử TOÀN BỘ pipeline train (tokenize → mask → LoRA → vòng train → lưu adapter)
trên một model TÍ HON khởi tạo ngẫu nhiên, dùng tokenizer thật của Qwen2.5 → chạy được trên CPU,
mất ~1–3 phút, không cần GPU và không cần tải model lớn.

    python train/smoke_test.py                          # mặc định: 20 bước, 48 mẫu, max_len 384
    python train/smoke_test.py --steps 5 --subset 16    # chạy siêu nhanh để kiểm tra môi trường

Mục đích: phát hiện lỗi cài đặt/dữ liệu TRƯỚC khi bỏ tiền thuê GPU để train thật.
"""

import argparse
import os
import sys
import time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct",
                    help="Chỉ dùng để lấy tokenizer (không tải trọng số model)")
    ap.add_argument("--data_dir", default="dataset")
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--subset", type=int, default=48)
    ap.add_argument("--max_len", type=int, default=384)
    ap.add_argument("--output_dir", default="out/smoke_test")
    ap.add_argument("--generate", action="store_true", help="Sau khi train, thử sinh 1 câu trả lời")
    args = ap.parse_args()

    from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM, Trainer, set_seed
    from datasets import load_dataset
    from train_lora import build_example, PadCollator, apply_lora, make_training_args, find_targets

    set_seed(0)
    print("=" * 70)
    print("SMOKE TEST – pipeline fine-tune trên CPU (model tí hon, tokenizer thật)")
    print("=" * 70)

    # 1) tokenizer thật
    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"
    print(f"[1/5] Tokenizer: {args.model} | vocab {len(tok)} | chat_template: {bool(tok.chat_template)}")

    # 2) dữ liệu
    train_file = os.path.join(args.data_dir, "train.jsonl")
    if not os.path.exists(train_file):
        sys.exit(f"Không thấy {train_file}. Chạy trước: python data/build_dataset.py --out {args.data_dir}")
    ds = load_dataset("json", data_files={"train": train_file})["train"]
    ds = ds.select(range(min(args.subset, len(ds))))
    ds = ds.map(lambda ex: build_example(tok, ex["messages"], args.max_len),
                remove_columns=ds.column_names, desc="Tokenize")
    ex = ds[0]
    n_learn = sum(1 for x in ex["labels"] if x != -100)
    print(f"[2/5] Dữ liệu: {len(ds)} mẫu | mẫu đầu {len(ex['input_ids'])} token, học {n_learn} token "
          f"(prompt bị mask = không tính loss)")

    # 3) model tí hon (cùng kiến trúc Qwen2, trọng số ngẫu nhiên → không tải model lớn)
    cfg = AutoConfig.from_pretrained(args.model)
    cfg.hidden_size, cfg.num_hidden_layers = 128, 2
    cfg.num_attention_heads, cfg.num_key_value_heads = 4, 2
    cfg.intermediate_size = 256
    cfg.max_position_embeddings = max(args.max_len + 64, 512)
    model = AutoModelForCausalLM.from_config(cfg)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[3/5] Model tí hon: {n_params/1e6:.2f}M tham số")

    model, targets = apply_lora(model, argparse.Namespace(
        load_in_4bit=False, target_modules=None, lora_r=8, lora_alpha=16, lora_dropout=0.05))
    print(f"[4/5] LoRA gắn vào: {', '.join(targets)}")

    # 4) train
    targs = make_training_args(
        output_dir=args.output_dir, max_steps=args.steps, per_device_train_batch_size=1,
        gradient_accumulation_steps=1, learning_rate=5e-4, logging_steps=5, save_strategy="no",
        eval_strategy="no", report_to=[], use_cpu=True, bf16=False, fp16=False,
        gradient_checkpointing=False, optim="adamw_torch",
    )
    t0 = time.time()
    trainer = Trainer(model=model, args=targs, train_dataset=ds,
                      data_collator=PadCollator(tok.pad_token_id), processing_class=tok)
    trainer.train()
    dt = time.time() - t0
    losses = [h["loss"] for h in trainer.state.log_history if "loss" in h]
    print(f"[5/5] Train xong {args.steps} bước trong {dt:.1f}s | loss: " +
          " → ".join(f"{l:.3f}" for l in losses[:6]) + (" ..." if len(losses) > 6 else ""))

    out = os.path.join(args.output_dir, "final")
    trainer.save_model(out)
    tok.save_pretrained(out)
    print(f"✓ Adapter thử nghiệm: {out}")

    # 5) thử load lại + sinh văn bản (kiểm tra đường ống suy luận)
    if args.generate:
        from peft import PeftModel
        base = AutoModelForCausalLM.from_config(cfg)
        m = PeftModel.from_pretrained(base, out)
        m.eval()
        msgs = [{"role": "system", "content": "Bạn là trợ lý bán giày."},
                {"role": "user", "content": "Chân 25cm đi size nào?"}]
        enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt")
        ids = enc["input_ids"] if hasattr(enc, "input_ids") else enc   # tương thích mọi phiên bản
        with torch.no_grad():
            gen = m.generate(ids, max_new_tokens=24, do_sample=False, pad_token_id=tok.pad_token_id)
        print("Sinh thử (model ngẫu nhiên nên chữ vô nghĩa — chỉ cần KHÔNG lỗi là đạt):")
        print("   ", tok.decode(gen[0][ids.shape[-1]:], skip_special_tokens=True).replace("\n", " ")[:160])

    print("=" * 70)
    print("KẾT LUẬN: pipeline OK. Giờ có thể train thật:")
    print("   python train/train_lora.py --model Qwen/Qwen2.5-3B-Instruct --load_in_4bit \\")
    print("       --data_dir dataset --output_dir out/shoebot-lora --epochs 3")
    print("=" * 70)


if __name__ == "__main__":
    main()
