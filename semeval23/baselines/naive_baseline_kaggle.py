"""
Naive Baseline (Kaggle 适配版)
==============================
忠实复刻 SemEval-2023 官方 naive baseline 的逻辑,但适配本课程的 Kaggle 格式。

官方原版 (pan-webis-de/pan-code/semeval23/baselines):
  - naive-baseline-task-1.py : 每条都预测 'passage'
  - naive-baseline-task-2.py : 每条都用链接网页标题 (targetTitle) 作为 spoiler
官方原版读取 'uuid' 字段、输出 run.jsonl (jsonl 格式),供 TIRA/Docker 平台使用。

本课程 Kaggle 的差异:
  - 数据用 'id' 字段(不是 'uuid')
  - 提交要求 CSV 格式:Task1 列为 (id, spoilerType);Task2 列为 (id, spoiler)
本脚本据此做了最小改动:把 uuid→id、jsonl→csv,逻辑与官方完全一致。

用法:
  python naive_baseline_kaggle.py <task1_test.jsonl> <task2_test.jsonl> <输出目录>
若只想跑其中一个,另一个参数传 "skip"。
"""
import json, sys, csv
from pathlib import Path

def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")]

def first(x):
    """targetTitle 可能是 str 或 list,统一成字符串。"""
    if isinstance(x, list):
        return " ".join(map(str, x))
    return str(x) if x is not None else ""

def naive_task1(test_path, out_path):
    """官方逻辑:每条都预测 passage。"""
    rows = load(test_path)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "spoilerType"])
        for e in rows:
            w.writerow([e["id"], "passage"])      # ← 官方 naive: 全部 passage
    print(f"[Task 1 naive] 写出 {out_path}  ({len(rows)} 行, 全部预测 passage)")

def naive_task2(test_path, out_path):
    """官方逻辑:每条都用 targetTitle 作为 spoiler。"""
    rows = load(test_path)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "spoiler"])
        for e in rows:
            title = first(e.get("targetTitle", "")).replace("\n", " ").strip()
            if not title:
                title = "spoiler"                  # 极少数空标题的兜底
            w.writerow([e["id"], title])           # ← 官方 naive: 用网页标题
    print(f"[Task 2 naive] 写出 {out_path}  ({len(rows)} 行, 全部用 targetTitle)")

if __name__ == "__main__":
    t1 = sys.argv[1] if len(sys.argv) > 1 else "skip"
    t2 = sys.argv[2] if len(sys.argv) > 2 else "skip"
    outdir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(".")
    outdir.mkdir(parents=True, exist_ok=True)

    if t1 != "skip":
        naive_task1(t1, outdir / "task1_naive_submission.csv")
    if t2 != "skip":
        naive_task2(t2, outdir / "task2_naive_submission.csv")
    print("完成。这两个 CSV 可直接提交到对应的 Kaggle 竞赛。")
