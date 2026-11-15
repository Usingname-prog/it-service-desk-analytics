# Verification & limitations

The repository contains synthetic ticket data only. No actual customer information or API credentials are required.

Reproduce with:
```bash
pip install -r requirements.txt
python -m service_analytics.pipeline --tickets 1500 --seed 42
python -m pytest -q
```

Expected output artifacts appear under `data/` and `reports/`, which are intentionally gitignored. No production results are claimed.

The model simplifies SLA logic by assessing resolved cases only; it does not compute the running SLA breach state of unresolved tickets.
