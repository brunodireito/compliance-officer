import re
import matplotlib.pyplot as plt
import numpy as np

INPUT_FILE = "compliance_report.md"

def parse_report(filename):
    """Extracts Topic names and Maturity Levels (0-3) from the Markdown."""
    data = {}
    with open(filename, "r") as f:
        content = f.read()
    
    # Regex to find "## Topic Name" and "**Nível Atingido:** X"
    # Adjust regex based on your exact markdown output format
    sections = content.split("## ")
    for section in sections[1:]:
        try:
            # Get Topic Name (first line)
            lines = section.strip().split("\n")
            topic = lines[0].strip()
            
            # Find Level
            level_match = re.search(r"Nível Atingido:\*\*.*?(\d)", section)
            if level_match:
                level = int(level_match.group(1))
                data[topic] = level
        except Exception:
            continue
            
    return data

def create_radar_chart(data):
    if not data:
        print("❌ No data found in report to plot.")
        return

    labels = list(data.keys())
    values = list(data.values())
    
    # Close the loop for the radar chart
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Draw the outline
    ax.plot(angles, values, color='#1a73e8', linewidth=2)
    ax.fill(angles, values, color='#1a73e8', alpha=0.25)
    
    # Fix axis to 0-5 levels
    ax.set_ylim(0, 3)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(["0", "1", "2", "3"], color="grey", size=10)
    
    # Labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=9, wrap=True)

    plt.title("Maturity Assessment Results", size=20, color='#1a73e8', y=1.1)
    
    # Save
    plt.savefig("maturity_chart.png")
    print("✅ Chart saved to 'maturity_chart.png'")
    plt.show()

if __name__ == "__main__":
    print(f"Reading {INPUT_FILE}...")
    data = parse_report(INPUT_FILE)
    print(f"Found {len(data)} topics.")
    create_radar_chart(data)