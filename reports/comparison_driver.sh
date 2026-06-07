set +e
cd /mnt/data/ai_agents_work/17
mkdir -p reports
echo '[agentic] run 1/1'
/opt/pyvenv/bin/python main.py --source target_code.py --test-output tests/test_generated.py --report-output reports/agentic_run_1.json --max-heal-attempts 2 --model gemini-2.5-flash --predictive-test-selection --base-ref 'HEAD~1' > reports/agentic_run_1.stdout.txt 2>&1
echo '[traditional] run 1/1'
/opt/pyvenv/bin/python - reports/traditional_run_1.json tests/test_research_suite.py <<'PYTRAD'
import json, subprocess, sys, time
from datetime import datetime, timezone
meta_path = sys.argv[1]
targets = sys.argv[2:]
command = [sys.executable, '-m', 'pytest', '-q', *targets]
start = time.time()
start_utc = datetime.now(timezone.utc).isoformat()
completed = subprocess.run(command, text=True, capture_output=True, check=False)
end = time.time()
end_utc = datetime.now(timezone.utc).isoformat()
output = '\n'.join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
payload = {'command': ' '.join(command), 'return_code': completed.returncode, 'passed': completed.returncode == 0, 'output': output, 'duration_seconds': round(end - start, 3), 'start_time_utc': start_utc, 'end_time_utc': end_utc}
open(meta_path, 'w', encoding='utf-8').write(json.dumps(payload, indent=2))
PYTRAD
exit 0
