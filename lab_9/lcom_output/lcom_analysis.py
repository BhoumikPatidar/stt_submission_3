import pandas as pd
import argparse

def analyze_lcom(csv_file, output_file, high_lcom_threshold=500):
    """
    Reads a CSV file with LCOM metrics for Java classes, computes summary statistics,
    identifies classes with high LCOM values (using LCOM1 as primary), and generates
    an analysis report including a Markdown table of the metrics.
    
    Parameters:
      csv_file (str): Path to the input CSV file.
      output_file (str): Path where the analysis report will be saved.
      high_lcom_threshold (float): Threshold above which LCOM1 is considered high.
    """
    # Read CSV file into a DataFrame.
    df = pd.read_csv(csv_file)
    
    # Compute average values for each LCOM metric.
    avg_lcom1 = df['LCOM1'].mean()
    avg_lcom2 = df['LCOM2'].mean()
    avg_lcom3 = df['LCOM3'].mean()
    avg_lcom4 = df['LCOM4'].mean()
    avg_lcom5 = df['LCOM5'].mean()
    avg_yalcom = df['YALCOM'].mean()
    
    # Identify classes with high LCOM1 values.
    high_lcom_classes = df[df['LCOM1'] > high_lcom_threshold]
    
    # Build the analysis report.
    report_lines = []
    report_lines.append("Java Class Cohesion Analysis Report")
    report_lines.append("=" * 50)
    report_lines.append("")
    
    report_lines.append("**Summary of LCOM Metrics (Averages):**")
    report_lines.append(f"- LCOM1: {avg_lcom1:.2f}")
    report_lines.append(f"- LCOM2: {avg_lcom2:.2f}")
    report_lines.append(f"- LCOM3: {avg_lcom3:.2f}")
    report_lines.append(f"- LCOM4: {avg_lcom4:.2f}")
    report_lines.append(f"- LCOM5: {avg_lcom5:.2f}")
    report_lines.append(f"- YALCOM: {avg_yalcom:.2f}")
    report_lines.append("")
    
    report_lines.append("**Interpretation:**")
    report_lines.append("A high LCOM value—especially a high LCOM1—indicates that a class's methods share few instance variables. "
                        "This suggests that the class may be undertaking multiple unrelated responsibilities, "
                        "making it a candidate for refactoring via functional decomposition to improve cohesion.")
    report_lines.append("")
    
    report_lines.append(f"**Classes with High LCOM1 Values (Threshold > {high_lcom_threshold}):**")
    if high_lcom_classes.empty:
        report_lines.append("None found.")
    else:
        for idx, row in high_lcom_classes.iterrows():
            report_lines.append(f"- **{row['Type Name']}** (Package: {row['Package Name']}) | LCOM1: {row['LCOM1']}")
    report_lines.append("")
    
    # Generate a Markdown table of all classes with their LCOM metrics.
    report_lines.append("**Detailed LCOM Metrics Table (Markdown Format):**")
    headers = df.columns.tolist()
    md_table = []
    md_table.append(" | ".join(headers))
    md_table.append(" | ".join(["---"] * len(headers)))
    for idx, row in df.iterrows():
        row_values = [str(row[col]) for col in headers]
        md_table.append(" | ".join(row_values))
    
    report_lines.extend(md_table)
    report_lines.append("")
    
    # Write the report to the output file.
    with open(output_file, "w") as f:
        f.write("\n".join(report_lines))
    
    print(f"Analysis complete. Report saved to '{output_file}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze Java class cohesion from LCOM CSV output and generate a report."
    )
    parser.add_argument("-i", "--input", required=True, help="Input CSV file with LCOM results.")
    parser.add_argument("-o", "--output", required=True, help="Output file for the analysis report.")
    parser.add_argument("-t", "--threshold", type=float, default=500, help="Threshold for high LCOM1 value.")
    args = parser.parse_args()
    
    analyze_lcom(args.input, args.output, args.threshold)
