#!/usr/bin/env python3
from tira.rest_api_client import Client
from pathlib import Path
import pandas as pd
from subprocess import check_output
import gzip
import shutil
from tqdm import tqdm

def truths():
    tira = Client()
    return Path(tira.download_dataset(task="pan26-generated-plagiarism-detection", dataset="generated-plagiarism-detection-20260315-training", truth_dataset=True))

MEASURES = ["ndcg_cut.10", "ndcg_cut.100", "recall.10", "recall.100", "recip_rank"]

def is_gz_file(filepath):
    with open(filepath, 'rb') as test_f:
        return test_f.read(2) == b'\x1f\x8b'

def normalize_gzip(filepath):
    if is_gz_file(filepath):
        with gzip.open(filepath, "rt") as f:
            tmp = f.read()
            

        with open(filepath, "w") as f:
            f.write(tmp)

def run_eval(i, qrels):
    for d in ["Ndcg@10", "Rr", "Docs Per Query (Avg)", "Docs Per Query (Min)", "Docs Per Query (Max)", "evaluation_run_id", "input_run_id",  "description", "internal_data"]:
        del i[d]

    run_file = Path("test-dataset-submissions") / i["flat-outputs"]
    eval_results = []
    for measure in MEASURES:
        normalize_gzip(str(run_file))
        cmd = ["trec_eval", "-q", "-m", measure, str(qrels), str(run_file)]

        eval_results.append(check_output(cmd).decode("utf-8"))

    i["eval_output"] = "test-dataset-submissions/trec-eval/" + run_file.name
    assert not Path(i["eval_output"]).is_file()
    Path(i["eval_output"]).parent.mkdir(exist_ok=True, parents=True)
    Path(i["eval_output"]).write_text("\n".join(eval_results))
    return i

def calculate_scores():
    qrels = truths() / "qrels.txt"
    ret = []

    shutil.rmtree("test-dataset-submissions/trec-eval", ignore_errors=True)
    for _, i in tqdm(list(pd.read_json("test-dataset-submissions/metadata.jsonl", lines=True).iterrows())):
        ret += [run_eval(i.to_dict(), qrels)]
    return ret

def embedd_to_tira_table(scores):
    lines = []
    covered = set()
    for l in scores:
        def load_score(measure):
            print(measure)
            tmp = Path(l["eval_output"]).read_text().split("\n")
            tmp = [i.replace(" ", "") for i in tmp if "all\t" in i]
            tmp = [i for i in tmp if f"{measure}\t" in i]
            assert len(tmp) == 1
            return float(tmp[0].split("\t")[-1])

        t = l["team"].replace("pan26-gen-maik-test", "baseline")
        a = (l["software"] if l["is_docker"] else Path(l["flat-outputs"]).name).replace("exponential-objective", "bm25")
        identifier = t + "-" + a
        if identifier in covered:
            continue
        covered.add(identifier)
        lines += [{
            "team": t,
            "approach": a,
            "recall_10": load_score("recall_10"),
            "recall_100": load_score("recall_100"),
            "ndcg_cut_10": load_score("ndcg_cut_10"),
            "ndcg_cut_100": load_score("ndcg_cut_100"),
            "recip_rank": load_score("recip_rank"),
        }]

    print(pd.DataFrame(lines).sort_values("recall_10"))

    return {
        "title": "Evaluation Results on the Main Test Set",
        "description": "The following table shows the evaluation results on the main test set for the 2026 edition of the Generative Plagiarism Detection at PAN. We show ndcg@10, ndcg@100, Recall@10, Recall@100, and the Reciprocal Rank. The submissions on a secondary dataset are still running, and we will update the results when the executions are finished.",
        "ev_keys": ["recall_10", "recall_100", "ndcg_cut_10", "ndcg_cut_100", "recip_rank"],
        "lines": lines,
        "table_headers": [
            {"title": "Team", "key": "team"},
            {"title": "Approach", "key": "approach"},
            {"title": "  ", "key": "does not exist"},
            {"title": "Recall@10", "key": "recall_10"},
            {"title": "Recall@100", "key": "recall_100"},
            {"title": "nDCG@10", "key": "ndcg_cut_10"},
            {"title": "nDCG@100", "key": "ndcg_cut_100"},
            {"title": "Reciprocal Rank", "key": "recip_rank"},
        ],
        "table_headers_small_layout": [
            {"title": "Team", "key": "team"},
            {"title": "Approach", "key": "approach"},
            {"title": "Recall@10", "key": "recall_10"},
        ],
        "table_sort_by": [{"key": "recall_10", "order": "desc"}],
    }


def upload_scores(scores):
    tira = Client()
    aggregated_results = [embedd_to_tira_table(scores)]
    tira.modify_task("pan26-generated-plagiarism-detection", {"aggregated_results": aggregated_results})


if __name__ == '__main__':
    scores = calculate_scores()
    upload_scores(scores)
