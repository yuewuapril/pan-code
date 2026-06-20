"""
Naive Baseline (Kaggle 适配版 · 自动定位版)
==========================================
忠实复刻 SemEval-2023 官方 naive baseline 的逻辑,但适配本课程的 Kaggle 格式。

官方原版 (pan-webis-de/pan-code/semeval23/baselines):
  - naive-baseline-task-1.py : 每条都预测 'passage'
  - naive-baseline-task-2.py : 每条都用链接网页标题 (targetTitle) 作为 spoiler

本课程 Kaggle 的差异:
  - 提交要求 CSV 格式:Task1 列为 (id, spoilerType);Task2 列为 (id, spoiler)
  - 数据字段可能是 'id' 也可能是 'uuid',本脚本两者都兼容

★ 自动定位:不传任何参数时,脚本自动读取「自己同目录下 data/test.jsonl」,
  输出写到「自己同目录下 output/」。无论你在哪个文件夹运行都不会报路径错。

用法:
  最简单(推荐) —— 在任意目录直接运行,自动找 data/test.jsonl:
      python <脚本路径>/naive_baseline_kaggle.py

  手动指定路径(可选):
      python naive_baseline_kaggle.py <task1_test.jsonl> <task2_test.jsonl> <输出目录>
      只想跑其中一个时,另一个参数传 "skip"。
"""
import json, sys, csv
from pathlib import Path

# 脚本自身所在目录 —— 自动定位的锚点,与「在哪运行」无关
HERE = Path(__file__).resolve().parent
DEFAULT_TEST = HERE / "data" / "test.jsonl"
DEFAULT_OUTDIR = HERE / "output"


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def get_id(e):
    """字段名兼容:本课程数据可能用 'id',官方原版用 'uuid'。"""
    if "id" in e:
        return e["id"]
    if "uuid" in e:
        return e["uuid"]
    raise KeyError("记录里既没有 'id' 也没有 'uuid' 字段,请检查数据格式。")


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
            w.writerow([get_id(e), "passage"])      # ← 官方 naive: 全部 passage
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
                title = "spoiler"                    # 极少数空标题的兜底
            w.writerow([get_id(e), title])           # ← 官方 naive: 用网页标题
    print(f"[Task 2 naive] 写出 {out_path}  ({len(rows)} 行, 全部用 targetTitle)")


if __name__ == "__main__":
    # 不传参数 → 自动用脚本同目录下的 data/test.jsonl 和 output/
    if len(sys.argv) <= 1:
        t1 = t2 = str(DEFAULT_TEST)
        outdir = DEFAULT_OUTDIR
        print(f"[自动定位] 未传参数,使用默认数据: {DEFAULT_TEST}")
        if not DEFAULT_TEST.exists():
            print(f"[错误] 没找到 {DEFAULT_TEST}")
            print(f"       请把 test.jsonl 放到: {HERE / 'data'} 目录下,或手动传入路径。")
            sys.exit(1)
    else:
        t1 = sys.argv[1] if len(sys.argv) > 1 else "skip"
        t2 = sys.argv[2] if len(sys.argv) > 2 else "skip"
        outdir = Path(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_OUTDIR

    outdir.mkdir(parents=True, exist_ok=True)

    if t1 != "skip":
        naive_task1(t1, outdir / "task1_naive_submission.csv")
    if t2 != "skip":
        naive_task2(t2, outdir / "task2_naive_submission.csv")
    print(f"完成。CSV 已写入 {outdir}/ ,可直接提交到对应的 Kaggle 竞赛。")
