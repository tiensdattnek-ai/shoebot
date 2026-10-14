#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evaluate.py – Chấm điểm model trước/sau khi fine-tune trên bộ câu hỏi kiểm thử.

    # 1) Model gốc (baseline)
    python eval/evaluate.py --model Qwen/Qwen2.5-3B-Instruct --out out/eval_baseline.md

    # 2) Model sau fine-tune
    python eval/evaluate.py --model Qwen/Qwen2.5-3B-Instruct \
        --adapter out/shoebot-lora/final --out out/eval_finetuned.md

Bộ câu hỏi: eval/eval_questions.jsonl, mỗi dòng {"question": ..., "keywords": [["nike","mỹ"], ...]}
Score = tỉ lệ nhóm từ khoá xuất hiện trong câu trả lời (không phân biệt hoa thường/dấu).
Keyword chỉ là chấm tự động — hãy ĐỌC câu trả lời trong file kết quả để chấm bằng mắt nữa.
"""

import argparse
import json
import os
import re
import sys
import unicodedata

import torch

SYSTEM = ("Bạn là ShoeBot – trợ lý bán hàng của một chuỗi bán lẻ giày/sneaker tại Việt Nam. "
          "Trả lời ngắn gọn, thân thiện, xưng 'em', gọi khách là 'anh/chị', thông tin thực tế, "
          "gợi ý bước tiếp theo để chốt đơn.")


def strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower()


def keyword_score(answer: str, keyword_groups) -> tuple:
    a = strip_accents(answer)
    hits, total = 0, max(1, len(keyword_groups))
    for group in keyword_groups:
        kws = [group] if isinstance(group, str) else group
        if any(strip_accents(k) in a for k in kws):
            hits += 1
    return hits / total, f"{hits}/{total}"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
    p.add_argument("--adapter", default=None, help="Đường dẫn LoRA adapter (bỏ trống = model gốc)")
    p.add_argument("--questions", default="eval/eval_questions.jsonl")
    p.add_argument("--out", default=None, help="File báo cáo (mặc định out/eval_<tag>.md)")
    p.add_argument("--max_new_tokens", type=int, default=320)
    p.add_argument("--load_in_4bit", action="store_true")
    p.add_argument("--limit", type=int, default=0, help="Chỉ chạy N câu đầu")
    p.add_argument("--device", default=None)
    return p.parse_args()


def main():
    args = parse_args()
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "train"))
    from train_lora import make_tokenizer, load_model  # dùng lại để tránh trùng code

    from transformers import AutoModelForCausalLM
    try:
        from peft import PeftModel
    except ImportError:
        PeftModel = None

    qs = [json.loads(l) for l in open(args.questions, encoding="utf-8") if l.strip()]
    if args.limit:
        qs = qs[:args.limit]

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    tok = make_tokenizer(args.model)

    print(f"→ Nạp model: {args.model}" + (f" + adapter {args.adapter}" if args.adapter else " (chưa fine-tune)"))
    model = load_model(args.model, args.load_in_4bit, for_training=False)
    if args.adapter:
        if PeftModel is None:
            sys.exit("Cần cài peft: pip install peft")
        model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()
    try:
        model.to(device)
    except Exception as e:
        print("(không chuyển được device, giữ nguyên):", e)

    tag = "finetuned" if args.adapter else "baseline"
    out_path = args.out or f"out/eval_{tag}.md"
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    jsonl_path = out_path.replace(".md", ".answers.jsonl")

    rows, total_score, total_kw = [], 0.0, 0
    for i, item in enumerate(qs, 1):
        msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": item["question"]}]
        enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt")
        ids = enc["input_ids"] if hasattr(enc, "input_ids") else enc
        ids = ids.to(model.device if hasattr(model, "device") else "cpu")
        with torch.no_grad():
            gen = model.generate(ids, max_new_tokens=args.max_new_tokens, do_sample=False,
                                 pad_token_id=tok.pad_token_id or tok.eos_token_id,
                                 eos_token_id=tok.eos_token_id)
        ans = tok.decode(gen[0][ids.shape[-1]:], skip_special_tokens=True).strip()
        score, kw = keyword_score(ans, item.get("keywords", []))
        total_score += score
        total_kw += 1
        rows.append({**item, "answer": ans, "score": round(score, 3), "keywords_hit": kw})
        print(f"[{i}/{len(qs)}] {kw:>5}  {item['question'][:70]}")

    avg = total_score / max(1, total_kw)
    lines = [f"# Kết quả đánh giá ShoeBot – {tag}", "",
             f"- Model: `{args.model}`" + (f" + adapter `{args.adapter}`" if args.adapter else ""),
             f"- Số câu: {len(rows)} | **Điểm trung bình: {avg*100:.1f}%**",
             f"- (Chấm theo nhóm từ khoá; hãy đọc câu trả lời để đánh giá chất lượng thật)", "",
             "| # | Câu hỏi | Điểm | Keyword đúng |", "|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        lines.append(f"| {i} | {r['question']} | {r['keywords_hit']} | {'✔' if r['score'] >= 0.5 else '✗'} |")
    lines += ["", "## Câu trả lời chi tiết", ""]
    for i, r in enumerate(rows, 1):
        lines += [f"### {i}. {r['question']}", "", f"> {r['answer']}", ""]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("-" * 70)
    print(f"ĐIỂM TRUNG BÌNH ({tag}): {avg*100:.1f}%")
    print(f"Báo cáo: {out_path}\nDữ liệu chi tiết: {jsonl_path}")


if __name__ == "__main__":
    main()
