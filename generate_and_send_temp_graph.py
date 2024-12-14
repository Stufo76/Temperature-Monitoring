#!/usr/bin/env python3

"""
Script to generate temperature graphs from Nagios service perfdata and send them via email.

Features:
- Extract data from Nagios perfdata output.
- Generate a temperature graph for selected hosts.
- Export data to Excel with formatting.
- Send the graph, data, and raw perfdata via email.

Configuration:
- Configure paths, email details, and hosts in a separate configuration file or as arguments.
- Tested with Nagios and `check_lenovo_xclarity` plugin.

Requirements:
- Nagios monitoring setup.
- `check_lenovo_xclarity` plugin: https://github.com/nickjeffrey/check_lenovo_xclarity
- Python libraries: pandas, matplotlib, pytz, smtplib, openpyxl.

Author: Diego Pastore
GitHub: https://github.com/Stufo76
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import shutil
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo
import argparse
import configparser

# Function to load configuration from a file
def load_config(config_file):
    """
    Load configuration settings from an external file.

    Parameters:
    - config_file (str): Path to the configuration file.

    Returns:
    - configparser.ConfigParser: A configuration object with the parsed settings.

    The configuration file should have sections like [Paths], [Email], and [Hosts].
    Example structure:
        [Paths]
        original_file = /path/to/original/file
        copied_file = /tmp/copied_file

        [Email]
        smtp_server = smtp.example.com
        smtp_port = 25
        from_email = sender@example.com
        to_email = recipient@example.com

        [Hosts]
        list = host1,host2
        colors = blue,green
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

# Function to send email with attachments
def send_email(subject, body, attachments, from_email, to_email, smtp_server, smtp_port):
    """
    Send an email with the specified subject, body, and attachments.

    Parameters:
    - subject (str): Subject line of the email.
    - body (str): Body content of the email.
    - attachments (list): List of file paths to attach to the email.
    - from_email (str): Email address of the sender.
    - to_email (str): Email address of the recipient.
    - smtp_server (str): Address of the SMTP server.
    - smtp_port (int): Port of the SMTP server.

    Raises:
    - Exception: If the email fails to send, the exception will be logged.
    """
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    # Attach files
    for file_path in attachments:
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
            msg.attach(part)

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(from_email, to_email, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to generate a temperature graph
def generate_graph(data, hosts, colors, graph_file, rome_tz):
    """
    Generate a temperature graph for the specified hosts and save it to a file.

    Parameters:
    - data (DataFrame): The dataset containing temperature details.
    - hosts (list): List of hostnames to include in the graph.
    - colors (list): List of colors corresponding to the hosts.
    - graph_file (str): Path where the graph image will be saved.
    - rome_tz (timezone): Timezone for converting timestamps.

    Notes:
    - Each host is assigned a specific color and plotted with its name as the label.
    - The colors and labels are determined by the order in the `hosts` and `colors` lists.
    """
    plt.figure(figsize=(10, 6))

    for host, color in zip(hosts, colors):
        host_data = data[data['Host'] == host].copy()
        if not host_data.empty:
            # Convert the 'Date' column from UTC to Europe/Rome timezone
            host_data['Date'] = host_data['Date'].dt.tz_localize('UTC').dt.tz_convert(rome_tz)
            plt.plot(host_data['Date'], host_data['Temperature'], label=host, color=color)

    plt.title('CED Temperature')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(graph_file)
    plt.close()

# Main function
def main():
    parser = argparse.ArgumentParser(description="Generate and send temperature graphs.")
    parser.add_argument('--config', type=str, required=True, help="Path to the configuration file.")
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Paths and settings
    original_file = config['Paths']['original_file']
    copied_file = config['Paths']['copied_file']
    graph_file = config['Paths']['graph_file']
    excel_file = config['Paths']['excel_file']

    smtp_server = config['Email']['smtp_server']
    smtp_port = int(config['Email']['smtp_port'])
    from_email = config['Email']['from_email']
    to_email = config['Email']['to_email']

    hosts = config['Hosts']['list'].split(',')
    colors = config['Hosts']['colors'].split(',')

    # Copy the original file to a temporary location
    shutil.copyfile(original_file, copied_file)
    # The original file is copied to avoid processing the live file, ensuring no data is lost during the process.
    # After copying, the original file is cleared to allow Nagios to start writing fresh data immediately.
    open(original_file, 'w').close()

    # Load and process the data
    data = pd.read_csv(copied_file, delimiter='\t', header=None,
                       names=['Timestamp', 'Host', 'Service', 'Status', 'Unknown', 'State', 'Metric1', 'Metric2', 'Details', 'Temperature_Detail'])

    # Extract the temperature values from the 'Temperature_Detail' field
    # Regex Explanation:
    # - 'Ambient_temperatureC=': Matches the static text preceding the temperature value.
    # - '([\d.]+)': Captures one or more digits (and optional decimals) representing the temperature value.
    # The captured group is converted to a float for numerical operations.
    data['Temperature'] = data['Temperature_Detail'].str.extract(r'Ambient_temperatureC=([\d.]+)').astype(float)

    data['Date'] = pd.to_datetime(data['Timestamp'], unit='s')

    # Generate graph
    rome_tz = pytz.timezone('Europe/Rome')
    generate_graph(data, hosts, colors, graph_file, rome_tz)

    # Prepare email
    subject = "CED Temperature Report"
    body = "Hello Team,\n\nPlease find attached the temperature graph and data.\n\nBest Regards,\nMonitoring Team"

    # Send email
    send_email(subject, body, [graph_file, copied_file], from_email, to_email, smtp_server, smtp_port)

    # Clean up temporary files
    os.remove(copied_file)
    os.remove(graph_file)

if __name__ == '__main__':
    main()
