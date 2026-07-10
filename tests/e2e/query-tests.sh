#!/bin/bash

# End-to-end testing: sending basic queries to Boagent /query endpoint with various parameters.
# Make sure that all containers (Boagent, BoaviztAPI and Scaphandre) are set up and running before using this script.

DATE=$(date +%s)
DATE_MINUS_ONE_MINUTE=$(date +%s --date '-1 min')

echo "Querying Boagent, for all impact criteria..."
curl 127.0.0.1:8000/query?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&verbose=false\&criteria=all > response_all_criteria.json

echo "Querying Boagent, for all impact criteria, and measuring power..."
curl 127.0.0.1:8000/query?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&verbose=false\&measure_power=true\&criteria=all > response_all_criteria_power.json

echo "Querying Boagent, for all impact criteria, measuring power and fetching hardware..."
curl 127.0.0.1:8000/query?start_time="$DATE_MINUS_ONE_MINUTE"\&end_time="$DATE"\&verbose=false\&measure_power=true\&fetch_hardware=true\&criteria=all > response_all_criteria_power_hardware.json
