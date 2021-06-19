# Screw
Scrapes peer IP addresses from torrents in `./torrents` directory (only supports UDP trackers) and writes them to `addresses.txt`
# Driver
Parses `addresses.txt` and runs nmap scan on them(`nmap -sC -sV`). Number of concurrent scans can be configured in the script. Writes scan reports to `report.txt` (appends, never rewrites). Generates log at `info.log`(again, appends). Writes IP addresses of completed scans to `completed.txt` (again, appends). `completed.txt` is checked every time a new scan starts.
