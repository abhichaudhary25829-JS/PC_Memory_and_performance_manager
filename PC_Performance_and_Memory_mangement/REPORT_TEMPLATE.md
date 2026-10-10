# Operating Systems CA Project Report
## PC Performance & Memory Management Suite

**Student:** [Enter your name]  
**Roll number / USN:** [Enter]  
**Course / Section:** [Enter]  
**Faculty:** [Enter]  
**Institution:** [Enter]

> Fill every bracketed item using your own measurements. Do not report sample numbers as experimental results unless you observed them on your machine.

## Abstract
This project extends a Python desktop PC Performance Monitor with a dedicated Smart Memory Analyzer. It displays CPU, RAM, GPU, temperature and storage indicators where supported, and adds detailed RAM availability, swap/page-file metrics, top memory-consuming processes, a configurable memory alert threshold, persistent SQLite memory history and CSV export. The system uses local measurements and does not require a cloud service.

## 1. Problem statement
Users may notice performance slowdowns without knowing whether RAM usage, CPU load, storage pressure or another monitored metric is elevated. The application provides a consolidated view and preserves observations for later analysis.

## 2. Objectives
1. Observe real system resource metrics.
2. Inspect visible processes and their memory use.
3. Record memory samples persistently.
4. Generate threshold alerts.
5. Export recorded samples and analyze trends.
6. Evaluate behavior using repeatable test cases.

## 3. Tools and technologies
Python, PySide6, psutil, SQLite, Matplotlib-like custom Qt chart widget, pytest, CSV.

## 4. Architecture
Operating system metrics → psutil collectors → snapshot → performance score and alert manager → PySide6 UI. The history module records time-stamped CPU/RAM/GPU/temperature/score and detailed RAM/swap samples in SQLite. The Memory Analyzer displays recent samples and exports CSV.

## 5. Features
- Dashboard: performance score and CPU, RAM, GPU, temperature and storage metrics.
- Processes: PID, process name, CPU percentage and resident memory.
- Memory Analyzer: used/available RAM, swap/page-file usage, recorded RAM chart, top memory-consuming processes, configurable RAM alert threshold and CSV export.
- History: average performance score, CPU/RAM averages and recent score chart.
- Alerts: timestamped warnings and critical events with cooldown protection.

## 6. Operating-system concepts
Explain physical memory, available memory, virtual memory/swap, process IDs, polling/sampling, system resource monitoring, alert thresholds and persistent data storage.

## 7. Experimental methodology
1. Record OS version and Python version.
2. Launch the application and note the starting time.
3. Observe dashboard readings and top memory processes.
4. Leave the application running for a measured interval.
5. Adjust the RAM alert threshold to a value that can be safely tested against the observed reading. Record whether the alert behavior matches the configured threshold.
6. Export memory history to CSV.
7. Repeat during ordinary different workloads, for example idle desktop and normal applications open.
8. Calculate min/max/average RAM utilization from the exported values.

## 8. Results table — complete with actual measurements

| Test | Condition | RAM % | Swap % | Result / evidence |
|---|---|---:|---:|---|
| 1 | Idle desktop | [measure] | [measure] | [screenshot/CSV row] |
| 2 | Normal applications open | [measure] | [measure] | [screenshot/CSV row] |
| 3 | Threshold check | [measure] | [measure] | [alert observed?] |
| 4 | After closing an unnecessary app | [measure] | [measure] | [before/after values] |

- Observation period: [start to end]
- Number of exported samples: [count CSV data rows]
- Minimum RAM utilization: [calculate]
- Maximum RAM utilization: [calculate]
- Average RAM utilization: [calculate]

Discuss only results supported by your data. Do not claim that high RAM usage automatically proves a performance fault.

## 9. Testing checklist

| Test | Expected behavior | Actual outcome |
|---|---|---|
| Application starts | Main window opens | [Pass/Fail + evidence] |
| Live dashboard | Values refresh | [Pass/Fail] |
| Process table | Visible processes listed | [Pass/Fail] |
| Memory analyzer | RAM/swap metrics appear | [Pass/Fail] |
| Memory chart | Recorded samples appear over time | [Pass/Fail] |
| Alert threshold | RAM alert uses configured threshold | [Pass/Fail] |
| CSV export | Actual stored samples exported | [Pass/Fail] |
| History persistence | Old rows remain after restart | [Pass/Fail] |
| Automated tests | pytest completes | [paste actual output] |

## 10. Limitations
- Sensor and process information depends on operating-system permissions and hardware support.
- Sampling can miss short-lived events.
- High memory usage alone does not prove a fault; operating systems use RAM for caching.
- GPU and temperature readings may be unavailable on some systems.
- CSV export includes only data actually recorded during the selected period.

## 11. Future work
Configurable sampling intervals, charts for more metrics, report generation, system tray mode, broader GPU support, and further process filters.

## 12. Conclusion
Summarize what worked on your machine, what your real observations showed, and the limitations encountered. Complete this section after testing.

## References
- psutil documentation: https://psutil.readthedocs.io/
- Python documentation: https://docs.python.org/3/
- Qt for Python: https://doc.qt.io/qtforpython/
- SQLite documentation: https://www.sqlite.org/docs.html
- Microsoft memory management: https://learn.microsoft.com/en-us/windows/win32/memory/memory-management
