def extract_slack_value(line):
    """Extract the slack value from a given line."""
    parts = line.split()
    return float(parts[-1])

def adjust_slack(violator, setup_threshold, hold_threshold):
    lines = violator.split('\n')
    setup_slack_line = next((line for line in lines if "Setup Slack:" in line), None)
    hold_slack_line = next((line for line in lines if "Hold Slack:" in line), None)
    
    if setup_slack_line and hold_slack_line:
        setup_slack = extract_slack_value(setup_slack_line)
        hold_slack = extract_slack_value(hold_slack_line)
        
        adjustment = 0
        data_path_adjustment = 0
        new_clock_period = 0

        if setup_slack < setup_threshold and hold_slack >= hold_threshold:
            # Case 1: Only setup slack is violated
            adjustment = setup_threshold - setup_slack
            new_hold_slack = hold_slack - adjustment
            if new_hold_slack >= hold_threshold:
                setup_slack = setup_threshold
                hold_slack = new_hold_slack
                lines = update_slack_values(lines, setup_slack, hold_slack)
        elif setup_slack >= setup_threshold and hold_slack < hold_threshold:
            # Case 2: Only hold slack is violated
            data_path_adjustment = hold_threshold - hold_slack
            new_setup_slack = setup_slack - data_path_adjustment
            if new_setup_slack >= setup_threshold:
                setup_slack = new_setup_slack
                hold_slack = hold_threshold
                lines = update_slack_values(lines, setup_slack, hold_slack)
        elif setup_slack < setup_threshold and hold_slack < hold_threshold:
            # Case 3: Both setup and hold slacks are violated
            new_clock_period = setup_threshold - setup_slack + hold_threshold - hold_slack
            adjustment = new_clock_period
            data_path_adjustment = hold_threshold - hold_slack
            setup_slack = setup_threshold
            hold_slack = hold_threshold
            lines = update_slack_values(lines, setup_slack, hold_slack)
            return "\n".join(lines), new_clock_period, data_path_adjustment, True

        return "\n".join(lines), adjustment, data_path_adjustment, False
    return violator, 0, 0, False

def update_slack_values(lines, setup_slack, hold_slack):
    """Update the slack values in the lines."""
    lines = [line.replace("Setup Slack:", f"Setup Slack: {setup_slack:.6f}") if "Setup Slack:" in line else line for line in lines]
    lines = [line.replace("Hold Slack:", f"Hold Slack: {hold_slack:.6f}") if "Hold Slack:" in line else line for line in lines]
    return lines

def main():
    setup_threshold = float(input("Enter setup threshold: "))
    hold_threshold = float(input("Enter hold threshold: "))
    adjusted_violators_file = "adjusted_violators.txt"
    summary_file = "adjustment_summary.txt"
    
    with open("violated_endpoints.txt", 'r') as file:
        content = file.read()
        violators = content.split("-----------------------")
    
    adjusted_violators = []
    adjustments_summary = []

    for violator in violators:
        adjusted_violator, adjustment, data_path_adjustment, is_both_violated = adjust_slack(violator, setup_threshold, hold_threshold)
        adjusted_violators.append(adjusted_violator)
        if adjustment > 0 or data_path_adjustment > 0:
            adjustments_summary.append((adjusted_violator, adjustment, data_path_adjustment, is_both_violated))
    
    with open(adjusted_violators_file, 'w') as out_file:
        for adjusted_violator in adjusted_violators:
            out_file.write(adjusted_violator)
            out_file.write("-----------------------\n")
    
    with open(summary_file, 'w') as summary_out:
        summary_out.write(f"Adjusted violators written to {adjusted_violators_file}\n")
        
        if adjustments_summary:
            summary_out.write("Adjustments summary:\n")
            for adjusted_violator, adjustment, data_path_adjustment, is_both_violated in adjustments_summary:
                if is_both_violated:
                    summary_out.write(f"Both setup and hold slacks are violated. Adjusting the clock period by {adjustment:.6f} and data path delay by {data_path_adjustment:.6f} will meet the thresholds.\n")
                else:
                    if adjustment > 0:
                        summary_out.write(f"Clock skew added: {adjustment:.6f}\n")
                    if data_path_adjustment > 0:
                        summary_out.write(f"Data path delay added: {data_path_adjustment:.6f}\n")
                summary_out.write(adjusted_violator)
                summary_out.write("-----------------------\n")

    print(f"Adjustment summary and adjusted violators written to {summary_file} and {adjusted_violators_file}, respectively.")

if __name__ == "__main__":
    main()
