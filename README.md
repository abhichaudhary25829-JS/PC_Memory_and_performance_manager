# 🖥️ PC Performance & Memory Management Suite

A Python desktop application for monitoring computer performance and exploring operating-system resource management. It provides a dark-themed dashboard for CPU, RAM, swap/page-file, GPU, temperature, storage, and running-process information.

> **Project type:** Operating Systems CA project  
> **Interface:** Desktop application  
> **Primary language:** Python

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation and Run](#installation-and-run)
- [Run from VS Code](#run-from-vs-code)
- [Application Pages](#application-pages)
- [Performance Score](#performance-score)
- [Data Storage and Privacy](#data-storage-and-privacy)
- [Testing](#testing)
- [Operating-System Concepts Demonstrated](#operating-system-concepts-demonstrated)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Troubleshooting](#troubleshooting)
- [Academic Use](#academic-use)

## Overview

The purpose of this project is to make system-resource information easier to observe and understand. It collects available system metrics, presents them in a graphical interface, records performance history locally, and highlights readings that cross configured thresholds.

The project demonstrates practical concepts related to operating systems, including process monitoring, memory utilization, resource observation, performance history, and threshold-based alerts.

**Important:** This is a monitoring and analysis tool. It does not increase physical RAM or replace the operating system's own resource manager.

## Features

### 1. Real-Time Dashboard

- CPU utilization
- CPU core and logical-thread information, where available
- RAM usage, total memory, used memory, and available memory
- Swap/page-file usage
- GPU utilization and VRAM information when supported
- Temperature readings when exposed by the hardware and drivers
- Storage capacity and disk activity information where available
- Performance score and recent usage charts

The interface refreshes system information approximately once per second.

### 2. Process Monitor

- Displays visible running processes
- Shows process ID (PID), process name, CPU usage, and memory usage
- Sorts processes by CPU usage
- Helps identify processes that are using significant resources

Some process information may not be available because of operating-system permissions.

### 3. Smart Memory Analyzer

- Shows physical RAM utilization and available memory
- Shows swap/page-file utilization
- Displays memory history collected while the application is running
- Helps identify processes with higher resident-memory usage
- Supports exporting recorded memory measurements to CSV

Historical data is not fabricated: the application can only show readings recorded while it was running.

### 4. Performance History

- Stores samples in a local SQLite database
- Displays historical performance information
- Provides summary statistics and recent charts
- Retains stored history across application restarts

### 5. Threshold-Based Alerts

The alert manager can generate warnings when monitored readings meet or exceed configured thresholds. Default thresholds in the current implementation are:

| Metric | Default threshold |
|---|---:|
| CPU usage | 90% |
| RAM usage | 90% |
| GPU utilization | 95% |
| Temperature | 85°C |
| Storage usage | 90% |

Alerts include a severity level and cooldown protection to reduce repeated notifications. Thresholds are defined in `src/alerts/alert_manager.py`.

A high reading is an indication to investigate, not automatic proof of a hardware fault.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| PySide6 / Qt | Desktop graphical user interface |
| psutil | CPU, memory, process, and storage metrics |
| NVIDIA Management Library (NVML) | NVIDIA GPU metrics when supported |
| SQLite | Local performance-history database |
| CSV | Exporting memory-history measurements |
| pytest | Automated tests |

## Project Structure

```text
PC-Performance-Memory-Management-Suite/
├── assets/
│   └── icon.svg
├── src/
│   ├── alerts/
│   │   └── alert_manager.py
│   ├── monitor/
│   │   ├── collector.py
│   │   ├── cpu.py
│   │   ├── gpu.py
│   │   ├── memory.py
│   │   ├── snapshot.py
│   │   ├── storage.py
│   │   └── temperature.py
│   ├── performance/
│   │   ├── history.py
│   │   └── score.py
│   ├── processes/
│   │   └── process_monitor.py
│   ├── ui/
│   │   ├── app.py
│   │   ├── theme.py
│   │   └── widgets.py
│   └── main.py
├── tests/
├── requirements.txt
├── pytest.ini
├── run.bat
├── run_existing_env.bat
├── CA_REPORT_TEMPLATE.md
├── VALIDATION.md
├── LICENSE
└── README.md
```

## Requirements

- Windows 10 or Windows 11 recommended for the supplied `.bat` launchers
- Python 3.10 or newer recommended
- Internet connection for the first dependency installation
- NVIDIA GPU monitoring requires a supported NVIDIA GPU, installed drivers, and NVML support

The application can run without NVIDIA GPU metrics; unsupported readings may be shown as unavailable.

## Installation and Run

### Option A — Recommended: One-click launch on Windows

1. Download and extract the project ZIP.
2. Open the extracted project folder.
3. Double-click **`run.bat`**.
4. On the first run, the launcher creates a `.venv` virtual environment if necessary.
5. It installs the packages in `requirements.txt` and starts the application.
6. Wait for the desktop window to appear.

The first launch may take several minutes depending on your internet speed and package installation. Keep the terminal window open while the application is running.

For later launches, use **`run_existing_env.bat`** after dependencies have been installed.

### Option B — Run from a terminal

Open a terminal in the project root directory and run:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.main
```

If the virtual environment already exists, you can run:

```powershell
.\.venv\Scripts\python.exe -m src.main
```

### Option C — Run from VS Code

1. Open the project folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Run the installation commands above if this is the first launch.
4. Start the app with `.\.venv\Scripts\python.exe -m src.main`.

Run commands from the folder containing `src`, `requirements.txt`, and `run.bat`.

## Application Pages

### Dashboard
Displays the main system metrics, performance score, and usage charts.

### Processes
Displays running processes and their CPU and memory usage.

### Memory Analyzer
Focuses on physical memory, swap/page-file usage, memory history, and high-memory processes.

### History
Shows recorded performance history and summary information.

### Alerts
Displays resource-threshold alerts generated by the monitoring logic.

The exact information available on each page depends on the hardware, operating system, drivers, and data collected during runtime.

## Performance Score

The application calculates a score between 0 and 100 using system-resource metrics. The score is an application-defined indicator intended to summarize the observed state; it is **not** an official Windows benchmark and should not be treated as a universal measurement of computer speed.

The calculation is implemented in:

```text
src/performance/score.py
```

## Data Storage and Privacy

The application is designed for local use. Its performance-history database is stored at:

```text
~/.pc-performance-monitor/history.db
```

On Windows, `~` resolves to the current user's home directory.

Memory-history export produces a CSV file that can be opened in spreadsheet software. Exported results contain recorded readings only. If the application was not running during a period, it cannot reconstruct measurements for that period.

System and process information can be sensitive. Review exported CSV files before sharing them.

## Testing

The project includes automated tests. From the project root, run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Alternatively, if your virtual environment is activated:

```bash
pytest -q
```

Record the actual test output in your CA report. Do not claim that a test passed unless you ran it and observed the result.

Recommended manual checks:

1. Confirm that the dashboard opens.
2. Compare CPU and RAM readings with Windows Task Manager.
3. Open the Processes page and confirm that visible process data is populated.
4. Open Memory Analyzer and verify RAM and swap values.
5. Leave the application running long enough to collect history.
6. Export memory history and inspect the CSV.
7. Verify threshold alerts using safe test conditions.
8. Restart the application and check whether saved history remains available.

## Operating-System Concepts Demonstrated

- **Process management:** observing running processes and their identifiers
- **Memory management:** observing physical RAM and swap/page-file usage
- **Resource monitoring:** collecting and presenting operating-system metrics
- **Performance analysis:** reviewing changes in metrics over time
- **Persistent storage:** saving recorded samples in SQLite
- **Threshold monitoring:** detecting resource readings that cross configured limits

This project is a monitoring application, not a CPU-scheduling, paging, synchronization, deadlock, or disk-scheduling simulator. Complete any separately assigned OS lab simulations required by your course rubric.

## Limitations

- Some metrics are unavailable on certain hardware or operating systems.
- Temperature and GPU readings depend on driver and sensor support.
- Process details can be restricted by permissions.
- Sampling can miss short-lived changes between updates.
- High RAM usage does not always mean a performance problem; the OS may use memory for caching.
- The performance score is a project-specific indicator, not a standardized benchmark.
- The application reports and records metrics; it does not guarantee that performance issues will be fixed.

## Future Improvements

- Additional GPU vendor support
- Configurable thresholds and sampling intervals through the UI
- More historical charts and selectable date ranges
- Automatic report generation from actual recorded samples
- System-tray mode
- More comprehensive integration and GUI tests

## Troubleshooting

### The app does not open
- Run `run.bat` from the extracted project folder.
- Keep the terminal open and read any error message.
- Confirm Python is installed by running `py --version`.
- Retry dependency installation with `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.

### A package installation fails
- Check your internet connection.
- Copy the final error message from the terminal.
- Avoid closing the terminal before the installation finishes.

### GPU or temperature data is unavailable
- Check whether the hardware and drivers expose the relevant metrics.
- NVIDIA GPU information requires compatible drivers and NVML support.
- Missing optional readings do not necessarily mean the rest of the application is broken.

### History appears empty
- Leave the application running to collect new samples.
- Confirm the database is writable in your user home directory.
- Remember that the application cannot display measurements from before it began recording.

## Academic Use

For the Operating Systems CA submission, include your own screenshots, test output, observation tables, and conclusions based on measurements collected on your computer. Explain the implementation in your own words and follow your faculty's report format.

## License

See the `LICENSE` file included with the project for license details.
