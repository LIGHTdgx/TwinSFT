# -*- coding: utf-8 -*-
"""train/lora_sft.py — LoRA SFT entry point (paper Sec. 3.3).

Backbone Qwen2.5-Coder-7B-Instruct (3B variant: Qwen2.5-Coder-3B-Instruct).
LoRA r=64, alpha=128, dropout 0.05; effective batch 32; 2 epochs; lr 1e-4;
max seq 2048; one A800, ~4 h per run. All five variants share these settings.
"""
import argparse

import torch
from peft import LoraConfig, get_peft_model
from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer,
                          TrainingArguments)


def build_model(base_model, r=64, alpha=128, dropout=0.05):
    tok = AutoTokenizer.from_pretrained(base_model)
    model = AutoModelForCausalLM.from_pretrained(
        base_model, torch_dtype=torch.bfloat16, device_map="auto")
    lcfg = LoraConfig(r=r, lora_alpha=alpha, lora_dropout=dropout,
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
                      task_type="CAUSAL_LM")
    model = get_peft_model(model, lcfg)
    model.print_trainable_parameters()
    return tok, model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True, help="twin_sft_corpus.json (data/build_corpus.py)")
    ap.add_argument("--base_model", default="Qwen/Qwen2.5-Coder-7B-Instruct")
    ap.add_argument("--out", default="ckpt/twin_sft_full")
    ap.add_argument("--epochs", type=float, default=2)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--batch", type=int, default=32)
    args = ap.parse_args()

    import json
    from torch.utils.data import Dataset

    SYSTEM_PROMPT = "你是一名资深安全审计专家，精通多语言代码审计与漏洞分析。"

    class SFTData(Dataset):
        def __init__(self, path):
            self.rows = json.load(open(path, encoding="utf-8"))

        def __len__(self):
            return len(self.rows)

        def __getitem__(self, i):
            r = self.rows[i]
            return {"messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": r["instruction"] + "\n" + r["input"]},
                {"role": "assistant", "content": r["output"]}]}

    tok, model = build_model(args.base_model)

    def collate(batch):
        texts = [tok.apply_chat_template(x["messages"], tokenize=False,
                                         add_generation_prompt=False) for x in batch]
        return tok(texts, return_tensors="pt", padding=True, truncation=True,
                   max_length=2048)

    trainer = Trainer(model=model, train_dataset=SFTData(args.corpus),
                      data_collator=collate,
                      args=TrainingArguments(
                          output_dir=args.out, num_train_epochs=args.epochs,
                          learning_rate=args.lr, per_device_train_batch_size=args.batch,
                          gradient_accumulation_steps=1, bf16=True, logging_steps=50,
                          save_strategy="epoch", report_to=[]))
    trainer.train()
    model.save_pretrained(args.out + "/final_adapter")
    tok.save_pretrained(args.out + "/final_adapter")


if __name__ == "__main__":
    main()
