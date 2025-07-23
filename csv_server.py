"""
CSV Reader

Example usage:
- 'What is in sample.csv?'
- 'how many columns are in sample.csv?'
- 'how many rows are in sample.csv?'
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from mcp.server import FastMCP

mcp = FastMCP("csv-reader-server")


def serialize_number(obj):
	"""Convert numpy numbers to Python native types"""
	if isinstance(obj, np.integer):
		return int(obj)
	if isinstance(obj, np.floating):
		return float(obj)
	raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


@mcp.tool()
def read_csv(file_path: str) -> str:
	"""
	Reads a CSV file and returns the contents
	Use when analyzing CSV files or reading csv files
	Example: 'read_csv sample.csv' 'what is in sample.csv?'
	:param file_path: Path to the CSV file, ask the user if not clear
	:return: JSON structure with file info, first 5 rows, and statistics
	"""
	try:
		file_path_obj = Path(file_path)
		if not file_path_obj.exists():
			return json.dumps(
				{"error": f"File '{file_path}' does not exist", "success": False}
			)
		if not file_path_obj.is_file():
			return json.dumps(
				{"error": f"File '{file_path}' is not a file", "success": False}
			)
		df = pd.read_csv(file_path_obj)
		numeric_stats = {}
		for col in df.select_dtypes(include=["int64", "float64"]).columns:
			numeric_stats[col] = {
				"mean": float(df[col].mean()),
				"min": float(df[col].min()),
				"max": float(df[col].max()),
			}
		response = {
			"success": True,
			"file_info": {
				"path": file_path,
				"column_count": int(len(df.columns)),
				"row_count": int(len(df)),
				"columns": list(df.columns),
			},
			"preview": {"first_5_rows": df.head().to_dict(orient="records")},
			"statistics": {"numeric_columns": numeric_stats},
		}
		return json.dumps(response, default=serialize_number, indent=2)

	except Exception as e:
		return json.dumps(
			{"error": f"Error reading file '{file_path}': {str(e)}", "success": False}
		)


if __name__ == "__main__":
	mcp.run()
