# Dataset versioning with DVC

Golden eval datasets are data, not code — they grow, get re-labeled, and need to
be reproducible per commit. Small example sets live in-repo (`examples/`); larger
golden sets are versioned with [DVC](https://dvc.org) so Git tracks a tiny
pointer while the bytes live in remote object storage (S3/GCS/Azure).

## One-time setup

```bash
pip install "dvc[s3]"          # or dvc[gs], dvc[azure]
dvc init                       # creates .dvc/ (commit it)
dvc remote add -d store s3://my-bucket/lleval-datasets
```

## Track a dataset

```bash
mkdir -p datasets
cp big-golden.jsonl datasets/
dvc add datasets/big-golden.jsonl     # creates datasets/big-golden.jsonl.dvc
git add datasets/big-golden.jsonl.dvc datasets/.gitignore
git commit -m "data: add big golden set v1"
dvc push                              # upload bytes to the remote
```

DVC writes a small `.dvc` pointer (md5 + size + path) and gitignores the data
file. The pointer is what Git versions — see `datasets/golden-large.jsonl.dvc`
for the shape.

## Reproduce on another machine / in CI

```bash
git pull
dvc pull                              # fetch the exact bytes for this commit
lleval run --config eval.yaml
```

In GitHub Actions, add a `dvc pull` step (with remote credentials in secrets)
before `lleval run` so the gate scores the pinned dataset version.

## Update a dataset

```bash
# edit datasets/big-golden.jsonl
dvc add datasets/big-golden.jsonl     # re-hashes; pointer changes
git commit -am "data: relabel ambiguous cases (v2)"
dvc push
```

Rolling back a dataset is `git checkout <rev> -- datasets/*.dvc && dvc checkout`.
