# Agent rules

Read `README.md` for how the pipeline and the web app fit together. The rules below come from mistakes made in this repo. When a rule has a check, the check is what counts. Keep this table in step with the checks: add a row when the owner corrects a new mistake, and drop a row once its mistake can no longer happen.

| Rule | What enforces it |
|---|---|
| Publish only live data. When a source fails, stop and write nothing. Never fall back to sample data. The 2026-11-16 and 2026-11-23 runs published sample numbers as real. | `build_data.py` exits on `SourceError`. The deploy job runs `python src/check_live.py web/dist/data/dashboard.json`. Tests: `test_a_failing_source_writes_nothing`, `test_the_deploy_check_refuses_sample_data_and_passes_live_data`. |
| Fetch every BOT date range through `bot_api.periods()`. Exchange Rates refuses more than 31 days. Statistics cuts long daily requests short and reports no error. | The build stops when a series has a gap wider than `MAX_GAP_DAYS` in `build_data.py`, and the message names `bot_api.periods()`. Test: `test_daily_statistics_survive_an_api_that_cuts_long_requests_short`. |
| A series that can reach zero or go negative, and every rate, uses `change="diff"`. | `series.py` asserts it for `unit="%"`. The build stops when a `pct` series has a value at or below zero. |
| A new indicator needs a line in `SERIES` and a shape in `sample_data.SHAPES`. | `test_sample_writes_every_series_in_the_shape_the_app_reads` fails with a `KeyError` when the shape is missing. |
| A change to the data file's shape changes `build_data.py` and the parser in `web/src/data.ts` in the same commit. | Partly by the parser tests in `web/src/derive.test.ts`. Nothing runs the parser on Python's output yet, so check by hand. |
| Never write a BOT token into code, a commit, or chat. Each BOT product reads its own variable, named in `bot_api.py`. | Judgment. |
| Merge or deploy only after the owner says so in chat. | Judgment. |
| After a UI change, look at the page in a browser at 375, 820 and 1440 px wide. | Judgment. |

Run the same checks as CI before you push:

```bash
pytest -q tests
python src/build_data.py --sample
cd web && npm test && npm run build
```
