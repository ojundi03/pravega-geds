nohup python3 latency-benchmark-runner.py &
echo "Gstreamer started at: $(date +%T)"
export start_time=$(date +%Y-%m-%d" "%H:%M:%S)
export logs_time=$(date -d "1 hour ago" +%Y-%m-%dT%H:%M:%SZ)
sleep 60
export pause_time=$(date +%Y-%m-%d" "%H:%M:%S)
./pause-tenant.sh 1700
export resume_time=$(date +%Y-%m-%d" "%H:%M:%S)
python3 clean_benchmark_scopes.py
sleep 60
rm -r test-nw-*
export end_time="$(date +%Y-%m-%d" "%H:%M:%S)"


./get-logs.sh $logs_time $start_time $end_time $pause_time $resume_time
echo "Run Complete."