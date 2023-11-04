def parse_timing_report(filename):
    data = []

    with open(filename, 'r') as file:
        lines = file.readlines()

    startpoint = None
    endpoint = None
    slack = None

    for line in lines:
        line = line.strip()

        # Extract startpoint
        if "Startpoint:" in line:
            startpoint = line.split("Startpoint:")[1].strip()

        # Extract endpoint
        elif "Endpoint:" in line:
            endpoint = line.split("Endpoint:")[1].strip()

        # Extract slack
        elif "slack" in line:
            slack = line.split("slack")[1].strip()

            # Once slack is found, add to data and reset for the next set
            data.append((startpoint, endpoint, slack))
            startpoint = None
            endpoint = None
            slack = None

    return data

# Parse setup timing report
data_setup = parse_timing_report("ifft_controller.timing.reg2reg.rpt")

# Parse hold timing report
data_hold = parse_timing_report("ifft_controller.timing_hold.reg2reg.rpt")

# Save parsed data from setup timing report
with open("setup_slacks.txt", "w") as outfile_setup:
    for idx, (start, end, sl) in enumerate(data_setup, 1):
        outfile_setup.write(f"setup_slack{idx}\n")
        outfile_setup.write(f"Startpoint: {start}\n")
        outfile_setup.write(f"Endpoint: {end}\n")
        outfile_setup.write(f"Slack: {sl}\n")
        outfile_setup.write("-----------------------\n")

# Save parsed data from hold timing report
with open("hold_slacks.txt", "w") as outfile_hold:
    for idx, (start, end, sl) in enumerate(data_hold, 1):
        outfile_hold.write(f"hold_slack{idx}\n")
        outfile_hold.write(f"Startpoint: {start}\n")
        outfile_hold.write(f"Endpoint: {end}\n")
        outfile_hold.write(f"Slack: {sl}\n")
        outfile_hold.write("-----------------------\n")

print("Parsing done and saved to setup_slacks.txt and hold_slacks.txt.")
