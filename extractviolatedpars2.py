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
        if setup_slack < setup_threshold:
            adjustment = setup_threshold - setup_slack
            setup_slack = setup_threshold
            hold_slack -= adjustment  # Adjusting hold slack
            lines = [line.replace("Setup Slack:", f"Setup Slack: {setup_slack:.6f}") if "Setup Slack:" in line else line for line in lines]
            lines = [line.replace("Hold Slack:", f"Hold Slack: {hold_slack:.6f}") if "Hold Slack:" in line else line for line in lines]
        
        return "\n".join(lines), hold_slack < hold_threshold, adjustment
    return violator, False, 0

def main():
    setup_threshold = float(input("Enter setup threshold: "))
    hold_threshold = float(input("Enter hold threshold: "))
    adjusted_violators_file = "adjusted_violators.txt"
    summary_file = "adjustment_summary.txt"
    
    with open("violated_endpoints.txt", 'r') as file:
        content = file.read()
        violators = content.split("-----------------------")
    
    adjusted_violators = []
    hold_violations_after_adjustment = []
    adjustment_summary = []

    for violator in violators:
        adjusted_violator, hold_violation, adjustment = adjust_slack(violator, setup_threshold, hold_threshold)
        adjusted_violators.append(adjusted_violator)
        if hold_violation:
            hold_violations_after_adjustment.append(adjusted_violator)
        if adjustment > 0:
            adjustment_summary.append((adjusted_violator, adjustment))
    
    with open(adjusted_violators_file, 'w') as out_file:
        for adjusted_violator in adjusted_violators:
            out_file.write(adjusted_violator)
            out_file.write("-----------------------\n")
    
    with open(summary_file, 'w') as summary_out:
        summary_out.write(f"Adjusted violators written to {adjusted_violators_file}\n")
        
        if adjustment_summary:
            summary_out.write("Adjustments made to fix setup violations:\n")
            for adjusted_violator, adjustment in adjustment_summary:
                summary_out.write(f"Clock skew added: {adjustment:.6f}\n")
                summary_out.write(adjusted_violator)
                summary_out.write("-----------------------\n")
        
        if hold_violations_after_adjustment:
            summary_out.write("Warning: Hold violations found after adjustment:\n")
            for violator in hold_violations_after_adjustment:
                summary_out.write(violator)
                summary_out.write("-----------------------\n")

    print(f"Adjustment summary and adjusted violators written to {summary_file} and {adjusted_violators_file}, respectively.")

if __name__ == "__main__":
    main()
