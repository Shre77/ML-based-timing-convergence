def extract_data_from_file(filename):
    data = {}
    with open(filename, 'r') as file:
        lines = file.readlines()

    slack_name, startpoint, endpoint, slack_value = None, None, None, None
    for line in lines:
        line = line.strip()
        if "setup_slack" in line or "hold_slack" in line:
            slack_name = line
        elif "Startpoint:" in line:
            startpoint = line.split("Startpoint:")[1].strip()
        elif "Endpoint:" in line:
            endpoint = line.split("Endpoint:")[1].strip()
        elif "Slack:" in line:
            slack_value = line.split("Slack:")[1].strip()

            # Once slack value is found, add to dictionary and reset for the next set
            data[endpoint] = (slack_name, startpoint, slack_value)
            slack_name, startpoint, endpoint, slack_value = None, None, None, None

    return data

# Extract data from both files
setup_data = extract_data_from_file("setup_slacks.txt")
hold_data = extract_data_from_file("hold_slacks.txt")

# Compare and store matches in a new file
with open("matching_endpoints.txt", "w") as outfile:
    for endpoint, (setup_name, setup_start, setup_slack) in setup_data.items():
        if endpoint in hold_data:
            hold_name, hold_start, hold_slack = hold_data[endpoint]
            outfile.write(f"{setup_name} & {hold_name}\n")
            outfile.write(f"Setup Startpoint: {setup_start}\n")
            outfile.write(f"Hold Startpoint: {hold_start}\n")
            outfile.write(f"Endpoint: {endpoint}\n")
            outfile.write(f"Setup Slack: {setup_slack}\n")
            outfile.write(f"Hold Slack: {hold_slack}\n")
            outfile.write("-----------------------\n")

print("Matching endpoints saved to matching_endpoints.txt.")
