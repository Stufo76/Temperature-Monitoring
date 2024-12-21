# Temperature Monitoring Script

[![GPLv3 License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://opensource.org/licenses/GPL-3.0)

This repository contains a Python script to automate the generation of temperature monitoring reports for IT infrastructure. The script processes performance data from Nagios, extracts temperature metrics, and produces:

- Time-series temperature graphs for selected hosts.
- Well-formatted Excel reports with detailed metrics.
- Automated email reports sent directly to the IT team.

## Features
- **Data Extraction**: Extract temperature data from Nagios `perfdata` files.
- **Visualization**: Generate time-series graphs for easy monitoring.
- **Excel Reporting**: Export detailed data to an Excel file with formatted tables.
- **Automated Email**: Send reports and graphs via email to the configured recipients.

## Requirements
- **Nagios Monitoring Setup** with the `check_lenovo_xclarity` plugin ([link](https://github.com/nickjeffrey/check_lenovo_xclarity)).
- Python libraries:
  - `pandas`
  - `matplotlib`
  - `pytz`
  - `smtplib`
  - `openpyxl`
- A working SMTP server for email distribution.

## Configuration
The script uses an external configuration file to set paths, email details, and hosts. Below is an example `config.ini` file:

```ini
[Paths]
original_file = /usr/local/nagios/var/service-perfdata.out
copied_file = /tmp/service-perfdata.out
graph_file = /tmp/CED_Temperature.png
excel_file = /tmp/CED_Temperature.xlsx

[Email]
smtp_server = smtp.example.com
smtp_port = 25
from_email = your-email@example.com
to_email = recipient@example.com

[Hosts]
list = host1,host2,host3
colors = blue,green,red
```

## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/Stufo76/Temperature-Monitoring.git
   ```

2. Install the required Python libraries:
   ```bash
   pip install pandas matplotlib pytz openpyxl
   ```

3. Edit the `config.ini` file to match your environment.

4. Run the script:
   ```bash
   python3 generate_and_send_temp_graph.py --config /path/to/config.ini
   ```

## Example Output
- **Graph**: A PNG file showing temperature trends for each host.
- **Excel Report**: A formatted Excel file with temperature data.

## License
This project is licensed under the GPL 3.0 License. See the `LICENSE` file for details.

## Author
**Diego Pastore**  
GitHub: [Stufo76](https://github.com/Stufo76)
