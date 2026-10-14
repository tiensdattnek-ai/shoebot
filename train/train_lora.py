#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
train_lora.py – Fine-tune LoRA/QLoRA cho ShoeBot (trợ lý bán hàng giày).

Ví dụ chạy trên máy có GPU (hoặc Google Colab T4):
    python train/train_lora.py --model Qwen/Qwen2.5-3B-Instruct --load_in_4bit \
        --data_dir dataset --output_dir out/shoebot-lora --epochs 3 \
        --batch_size 2 --grad_accum 8 --max_len 1024

Test nhanh pipeline không cần GPU (model nhỏ, 20 bước):
    python train/smoke_test.py

Sau khi train xong, adapter nằm ở: <output_dir>/final
Dùng thử: python app/chat_cli.py --model Qwen/Qwen2.5-3B-Instruct --adapter out/shoebot-lora/final
"""

import argparse
import dataclasses
import json
import os
import sys

import torch

# ============================================================ ĐỌC THAM SỐ
def parse_args():
    p = argparse.ArgumentParser(description="Fine-tune LoRA cho model hỏi đáp giày")
    p.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct",
                   help="Model gốc trên HuggingFace (Qwen2.5-1.5B/3B/7B-Instruct, Vistral, Llama-3.2...)")
    p.add_argument("--data_dir", default="dataset", help="Thư mục chứa train.jsonl/val.jsonl")
    p.add_argument("--output_dir", default="out/shoebot-lora")
    p.add_argument("--epochs", type=float, default=3)
    p.add_argument("--max_steps", type=int, default=-1, help=">0 thì dừng theo số bước (dùng để test nhanh)")
    p.add_argument("--batch_size", type=int, default=2, help="Batch mỗi thiết bị")
    p.add_argument("--grad_accum", type=int, default=8)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--max_len", type=int, default=1024)
    p.add_argument("--lora_r", type=int, default=16)
    p.add_argument("--lora_alpha", type=int, default=32)
    p.add_argument("--lora_dropout", type=float, default=0.05)
    p.add_argument("--target_modules", default=None,
                   help="Mặc định tự dò (q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj...)")
    p.add_argument("--load_in_4bit", action="store_true", help="QLoRA 4-bit (tiết kiệm VRAM, cần bitsandbytes)")
    p.add_argument("--gradient_checkpointing", action="store_true", default=True)
    p.add_argument("--no_gradient_checkpointing", dest="gradient_checkpointing", action="store_false")
    p.add_argument("--subset", type=int, default=0, help="Chỉ dùng N mẫu đầu (để test nhanh)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--logging_steps", type=int, default=10)
    p.add_argument("--eval_strategy", default="epoch", choices=["epoch", "steps", "no"])
    p.add_argument("--save_strategy", default="epoch", choices=["epoch", "steps", "no"])
    p.add_argument("--no_eval", action="store_true", help="Bỏ qua tập validation")
    return p.parse_args()


# ============================================================ TOKENIZE + MASK
def make_tokenizer(model_id, local_files_only=False):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id, local_files_only=local_files_only, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"
    return tok


def build_example(tok, messages, max_len):
    """
    Trả về dict {input_ids, labels}:
    - input_ids: toàn bộ hội thoại theo chat template
    - labels: -100 cho phần system/user (không tính loss) + phần pad; giữ token của assistant
    """
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    enc = tok(text, add_special_tokens=False, truncation=True, max_length=max_len,
              return_offsets_mapping=getattr(tok, "is_fast", False))
    ids = enc["input_ids"]
    offsets = enc.get("offset_mapping")

    # tìm khoảng ký tự của từng câu trả lời assistant
    spans, pos = [], 0
    for m in messages:
        c = m.get("content", "")
        if not c:
            continue
        idx = text.find(c, pos)
        if idx < 0:
            idx = text.find(c)
        if idx < 0:
            continue
        if m.get("role") == "assistant":
            spans.append((idx, idx + len(c)))
        pos = idx + len(c)

    if offsets is not None and spans:
        labels = []
        for (s, e), tid in zip(offsets, ids):
            if e <= s:                       # token đặc biệt (không có vị trí ký tự)
                labels.append(-100)
                continue
            keep = any(s < ae and e > as_ for as_, ae in spans)
            labels.append(tid if keep else -100)
    else:
        # fallback: mask theo prompt (mọi thứ trước lượt assistant cuối)
        prompt_text = tok.apply_chat_template(messages[:-1], tokenize=False, add_generation_prompt=True)
        prompt_ids = tok(prompt_text, add_special_tokens=False)["input_ids"]
        n = len(prompt_ids)
        if ids[:n] == prompt_ids:
            labels = [-100] * n + list(ids[n:])
        else:
            labels = list(ids)  # không mask được → học cả hội thoại (vẫn train được)
    return {"input_ids": ids, "labels": labels}


class PadCollator:
    """Padding cho input_ids/labels (labels dùng -100 cho phần pad)."""
    def __init__(self, pad_id, pad_to_multiple_of=8):
        self.pad_id = pad_id
        self.pad_to_multiple_of = pad_to_multiple_of

    def __call__(self, features):
        maxlen = max(len(f["input_ids"]) for f in features)
        if self.pad_to_multiple_of:
            m = self.pad_to_multiple_of
            maxlen = ((maxlen + m - 1) // m) * m
        batch = {"input_ids": [], "attention_mask": [], "labels": []}
        for f in features:
            pad = maxlen - len(f["input_ids"])
            batch["input_ids"].append(list(f["input_ids"]) + [self.pad_id] * pad)
            batch["attention_mask"].append([1] * len(f["input_ids"]) + [0] * pad)
            batch["labels"].append(list(f["labels"]) + [-100] * pad)
        return {k: torch.tensor(v, dtype=torch.long) for k, v in batch.items()}


# ============================================================ MODEL + LORA
def load_model(model_id, load_in_4bit, for_training=True):
    from transformers import AutoModelForCausalLM
    kwargs = dict(trust_remote_code=True, low_cpu_mem_usage=True)
    try:  # transformers >= 4.56 dùng 'dtype'; bản cũ dùng 'torch_dtype'
        kwargs["dtype"] = torch.bfloat16 if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else (
            torch.float16 if torch.cuda.is_available() else torch.float32)
        if load_in_4bit:
            from transformers import BitsAndBytesConfig
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16)
        model = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
    except TypeError:
        kwargs.pop("dtype", None)
        kwargs["torch_dtype"] = torch.float32 if not torch.cuda.is_available() else torch.float16
        model = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
    return model


def find_targets(model, wanted=("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")):
    names = {n.split(".")[-1] for n, _ in model.named_modules()}
    found = [w for w in wanted if w in names]
    if not found:
        for cand in ("c_attn", "c_proj", "query", "key", "value", "dense"):
            if cand in names:
                found.append(cand)
    return found


def apply_lora(model, args):
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
    if args.load_in_4bit:
        model = prepare_model_for_kbit_training(model)
    targets = ([t.strip() for t in args.target_modules.split(",")] if args.target_modules
               else find_targets(model))
    if not targets:
        raise SystemExit("Không tìm thấy module để gắn LoRA — hãy truyền --target_modules thủ công.")
    cfg = LoraConfig(r=args.lora_r, lora_alpha=args.lora_alpha, lora_dropout=args.lora_dropout,
                     bias="none", task_type=TaskType.CAUSAL_LM, target_modules=targets)
    model = get_peft_model(model, cfg)
    return model, targets


def make_training_args(**kw):
    """Lọc kwargs theo phiên bản transformers (v4 dùng evaluation_strategy, v5 dùng eval_strategy)."""
    from transformers import TrainingArguments
    fields = {f.name for f in dataclasses.fields(TrainingArguments)}
    kw = {k: v for k, v in kw.items() if k in fields}
    if "eval_strategy" not in fields and "evaluation_strategy" in fields:
        kw["evaluation_strategy"] = kw.pop("eval_strategy", "no")
    return TrainingArguments(**kw)


# ============================================================ MAIN
def main():
    args = parse_args()
    from transformers import Trainer, set_seed
    from datasets import load_dataset

    set_seed(args.seed)
    train_file = os.path.join(args.data_dir, "train.jsonl")
    val_file = os.path.join(args.data_dir, "val.jsonl")
    if not os.path.exists(train_file):
        sys.exit(f"Không thấy {train_file}. Chạy: python data/build_dataset.py --out {args.data_dir}")

    print("=" * 70)
    print("SHOEBOT – FINE-TUNE LORA")
    print("=" * 70)
    print(f"Model        : {args.model}")
    print(f"Dữ liệu      : {train_file}")
    print(f"Thiết bị     : {'GPU: ' + torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU (rất chậm — nên dùng Colab/GPU)'}")
    print(f"4-bit QLoRA  : {args.load_in_4bit}")
    print("-" * 70)

    tok = make_tokenizer(args.model)

    # ---------- dữ liệu
    data_files = {"train": train_file}
    if os.path.exists(val_file) and not args.no_eval:
        data_files["validation"] = val_file
    raw = load_dataset("json", data_files=data_files)
    if args.subset:
        for k in raw:
            raw[k] = raw[k].select(range(min(args.subset, len(raw[k]))))

    def _tok(ex):
        return build_example(tok, ex["messages"], args.max_len)

    cols = raw["train"].column_names
    ds = raw.map(_tok, remove_columns=cols, desc="Tokenize")

    # kiểm tra masking 1 mẫu
    ex0 = ds["train"][0]
    learn = sum(1 for x in ex0["labels"] if x != -100)
    print(f"[kiểm tra] Mẫu đầu: {len(ex0['input_ids'])} token | học {learn} token | mask {len(ex0['labels']) - learn}")
    print("[kiểm tra] Đuôi câu trả lời được học:",
          tok.decode([x for x in ex0["labels"] if x != -100][-40:])[:200].replace("\n", " "))

    # ---------- model
    model = load_model(args.model, args.load_in_4bit)
    if args.gradient_checkpointing and torch.cuda.is_available():
        model.gradient_checkpointing_enable()
        if hasattr(model, "enable_input_require_grads"):
            model.enable_input_require_grads()
    model, targets = apply_lora(model, args)
    model.print_trainable_parameters()
    print("LoRA gắn vào  :", ", ".join(targets))

    # ---------- huấn luyện
    use_cuda = torch.cuda.is_available()
    targs = make_training_args(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=max(1, args.batch_size),
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=args.logging_steps,
        eval_strategy=("no" if (args.no_eval or "validation" not in ds) else args.eval_strategy),
        save_strategy=("no" if args.max_steps > 0 else args.save_strategy),
        save_total_limit=2,
        bf16=(use_cuda and torch.cuda.is_bf16_supported()),
        fp16=(use_cuda and not torch.cuda.is_bf16_supported()),
        gradient_checkpointing=(args.gradient_checkpointing and use_cuda),
        optim=("paged_adamw_8bit" if args.load_in_4bit else "adamw_torch"),
        report_to=[],
        seed=args.seed, data_seed=args.seed,
        use_cpu=not use_cuda,
        dataloader_pin_memory=use_cuda,
    )

    trainer_kwargs = dict(model=model, args=targs, train_dataset=ds["train"],
                          data_collator=PadCollator(tok.pad_token_id))
    if "validation" in ds:
        trainer_kwargs["eval_dataset"] = ds["validation"]
    try:      # transformers v5: processing_class; v4: tokenizer
        trainer = Trainer(processing_class=tok, **trainer_kwargs)
    except TypeError:
        trainer = Trainer(tokenizer=tok, **trainer_kwargs)

    trainer.train()

    # ---------- lưu adapter
    out_final = os.path.join(args.output_dir, "final")
    os.makedirs(out_final, exist_ok=True)
    trainer.save_model(out_final)
    tok.save_pretrained(out_final)
    log = {
        "model": args.model, "lora": {"r": args.lora_r, "alpha": args.lora_alpha,
                                      "dropout": args.lora_dropout, "targets": targets},
        "epochs": args.epochs, "lr": args.lr, "max_len": args.max_len,
        "load_in_4bit": args.load_in_4bit, "batch_size": args.batch_size, "grad_accum": args.grad_accum,
        "n_train": len(ds["train"]), "n_val": len(ds.get("validation", [])),
        "history": trainer.state.log_history,
    }
    with open(os.path.join(args.output_dir, "train_log.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)

    print("-" * 70)
    print(f"✓ XONG. Adapter đã lưu tại: {out_final}")
    print("Dùng thử:")
    print(f"  python app/chat_cli.py --model {args.model} --adapter {out_final}")
    print(f"  python eval/evaluate.py --model {args.model} --adapter {out_final}")


if __name__ == "__main__":
    main()
