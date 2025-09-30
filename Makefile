# WHY: One-command tasks keep runs reproducible.

.PHONY: setup ingest asr train verify serve lint test

setup:
	pip install -r requirements.txt

ingest:
	python -m src.etl.ingest --input urls.txt --out data/raw

asr:
	python -m src.asr.transcribe --in data/raw --out data/asr

train:
	python -m src.nlp.train --cfg configs/text_baseline.yaml

verify:
	python -m src.retriever.verify --in data/asr --out artifacts/evidence

serve:
	python -m uvicorn src.ui.api:app --reload --port 8000

lint:
	ruff check .

test:
	PYTHONPATH=. pytest -q