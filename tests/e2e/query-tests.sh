#!/bin/bash

# End-to-end testing: sending basic queries to Boagent /query endpoint with various parameters.
# Make sure that all containers (Boagent, BoaviztAPI and Scaphandre) are set up and running before using this script.

DATE=$(date +%s)
DATE_MINUS_ONE_MINUTE=$(date +%s --date '-1 min')

# Provide the PID of a process as first argument to query data related to this process
# If the process in question has not been evaluated by Scaphandre, Boagent will not return any data.
PROCESS_ID=$1

echo "Querying Boagent, for all impact criteria..."
curl 127.0.0.1:8000/query?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&verbose=false\&criteria=all > response_all_criteria.json

echo "Querying Boagent, for all impact criteria, and measuring power..."
curl 127.0.0.1:8000/query?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&verbose=false\&measure_power=true\&criteria=all > response_all_criteria_power.json

echo "Querying Boagent, for all impact criteria, measuring power and fetching hardware..."
curl 127.0.0.1:8000/query?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&verbose=false\&measure_power=true\&fetch_hardware=true\&criteria=all > response_all_criteria_power_hardware.json

echo "Querying Boagent, for all impact criteria, measuring power and fetching hardware, in verbose mode..."
curl 127.0.0.1:8000/query?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&verbose=true\&measure_power=true\&fetch_hardware=true\&criteria=all > response_all_criteria_power_hardware_verbose.json

echo "Querying Boagent, for all impact criteria, in Prometheus format..."
curl 127.0.0.1:8000/metrics?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&verbose=false\&criteria=all > response_prometheus_all_criteria.json

echo "Querying Boagent, for all impact criteria, and measuring power, in Prometheus format..."
curl 127.0.0.1:8000/metrics?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&verbose=false\&measure_power=true\&criteria=all > response_prometheus_all_criteria_power.json

echo "Querying Boagent, for all impact criteria, measuring power and fetching hardware, in Prometheus format..."
curl 127.0.0.1:8000/metrics?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&verbose=false\&measure_power=true\&fetch_hardware=true\&criteria=all > response_prometheus_all_criteria_power_hardware.json

echo "Querying Boagent, for all impact criteria, measuring power and fetching hardware, in verbose mode, in Prometheus format..."
curl 127.0.0.1:8000/metrics?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&verbose=true\&measure_power=true\&fetch_hardware=true\&criteria=all > response_prometheus_all_criteria_power_hardware_verbose.json

if [ "$#" -eq 1 ]; then
	echo "Querying Boagent, for process embedded impacts..."
	curl 127.0.0.1:8000/process_embedded_impacts?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&process_id="$PROCESS_ID"\&fetch_hardware=true > response_process_embedded_impacts.json
fi
