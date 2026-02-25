#!/usr/bin/env bash
set -euo pipefail

required_dirs=(
  "run/conf/callbacks"
  "run/conf/data"
  "run/conf/model"
  "run/conf/trainer"
  "run/pipeline/training"
  "data/raw"
  "data/processed"
  "src/data_module"
  "src/model_module"
  "src/trainer_module"
  "src/eval_module"
  "src/utils"
  "scripts"
  "tests"
  "notebooks"
  "figures/final"
  "outputs/checkpoints"
  "outputs/logs"
  "outputs/figures"
  "docs/plan"
  "docs/Data"
  "docs/problem_formulation"
  "docs/reference_original"
  "docs/reference_conclu"
  "docs/prompts"
)

missing=0
for d in "${required_dirs[@]}"; do
  if [[ ! -d "$d" ]]; then
    echo "MISSING: $d"
    missing=1
  fi
done

if [[ "$missing" -eq 0 ]]; then
  echo "Structure check passed."
else
  echo "Structure check failed."
  exit 1
fi
