# Screw
Scrapes peer IP addresses from torrents (only supports UDP trackers) and writes them to `addresses.txt`
# Driver
Parses `addresses.txt` and runs nmap scans on them. Number of concurrent scans can be configured in the script. Writes scan reports to `report.txt` (appends, never rewrites). Generates log at `info.log`. Writes IP addresses of completed scans to `completed.txt` (again, appends). `complted.txt` is checked every time a new scan starts.
