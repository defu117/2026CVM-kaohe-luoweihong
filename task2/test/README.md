# Test Scenario

Run this script after the profiler container has started:

```bash
bash task2/test/test_scenario.sh
```

Record the printed start/end timestamps, then query the same interval in the Web UI or CLI. The generated flame graph should show CPU-heavy `stress-ng` frames when `stress-ng` is available.

Place verification screenshots in `task2/test/screenshots/`.

