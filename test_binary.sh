#!/bin/bash
cd /Users/danuta.paraficz/PyProjects/planner_osteo/dist

echo "=== Testing Binary: Validation ==="
printf "2\n\n0\n" | ./PlannerAllInOne 2>&1 | grep -A 3 "VALIDATION"
echo ""

echo "=== Testing Binary: Visualize Input ==="
printf "4\n\n0\n" | ./PlannerAllInOne 2>&1 | grep "✓"
echo ""

echo "=== Testing Binary: Run Scheduler (sample output) ==="
# Just start it and capture first few lines
(printf "3\n" | ./PlannerAllInOne 2>&1 | head -30) &
PID=$!
sleep 5
kill $PID 2>/dev/null
echo ""

echo "=== Binary Tests Complete ==="
