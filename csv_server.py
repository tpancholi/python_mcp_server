"""
CSV Reader

Example usage:
- 'What is in sample.csv?'
- 'how many columns are in sample.csv?'
- 'how many rows are in sample.csv?'
- 'sum sales by region in sales.csv'
- 'give me average price by category in products.csv'
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from mcp.server import FastMCP

mcp = FastMCP("csv-reader-server")


def serialize_number(obj):
	"""Convert numpy/pandas numbers and timestamps to Python native types"""
	if isinstance(obj, np.integer) or pd.api.types.is_integer_dtype(obj):
		return int(obj)
	if isinstance(obj, np.floating) or pd.api.types.is_float_dtype(obj):
		return float(obj)
	if isinstance(obj, (np.ndarray, pd.Series)):
		return obj.tolist()
	if isinstance(obj, pd.Timestamp) or pd.api.types.is_datetime64_any_dtype(obj):
		return obj.isoformat()
	if pd.isna(obj):
		return None
	if isinstance(obj, bytes):
		return obj.decode("utf-8")
	raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


@mcp.tool()
def read_csv(file_path: str) -> str:
	"""
	Reads a CSV file and returns the contents with detailed analysis
	Use when analyzing CSV files or reading csv files
	Example: 'read_csv sample.csv' 'what is in sample.csv?'
	:param file_path: Path to the CSV file, ask the user if not clear
	:return: JSON structure with file info, preview, statistics, and metadata
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

		# Read CSV with encoding fallback
		try:
			df = pd.read_csv(file_path_obj)
		except UnicodeDecodeError:
			df = pd.read_csv(file_path_obj, encoding="utf-8-sig")

		# Calculate statistics for numeric columns
		numeric_stats = {}
		for col in df.select_dtypes(include=["int64", "float64"]).columns:
			numeric_stats[col] = {
				"mean": float(df[col].mean()),
				"median": float(df[col].median()),
				"min": float(df[col].min()),
				"max": float(df[col].max()),
				"std": float(df[col].std()),
				"null_count": int(df[col].isnull().sum()),
			}

		# Get column types and null counts
		column_info = {
			col: {
				"type": str(df[col].dtype),
				"null_count": int(df[col].isnull().sum()),
				"unique_values": int(df[col].nunique()),
			}
			for col in df.columns
		}

		response = {
			"success": True,
			"file_info": {
				"path": str(file_path_obj),
				"size_bytes": file_path_obj.stat().st_size,
				"last_modified": pd.Timestamp(
					file_path_obj.stat().st_mtime, unit="s"
				).isoformat(),
				"column_count": int(len(df.columns)),
				"row_count": int(len(df)),
				"columns": list(df.columns),
			},
			"preview": {
				"first_5_rows": df.head().to_dict(orient="records"),
				"last_5_rows": df.tail().to_dict(orient="records"),
			},
			"statistics": {
				"numeric_columns": numeric_stats,
				"memory_usage": {
					"total": int(df.memory_usage(deep=True).sum()),
					"per_column": df.memory_usage(deep=True).to_dict(),
				},
			},
			"schema": {"columns": column_info},
			"metadata": {
				"timestamp": pd.Timestamp.now().isoformat(),
				"pandas_version": pd.__version__,
			},
		}
		return json.dumps(response, default=serialize_number, indent=2)

	except Exception as e:
		return json.dumps(
			{
				"error": f"Error processing file '{file_path}': {str(e)}",
				"success": False,
				"exception_type": type(e).__name__,
			}
		)


@mcp.tool()
def aggregate_csv(
	file_path: str, group_by: str, agg_column: str, agg_function: str
) -> str:
	"""
	Aggregates data in a CSV file to return total, mean, median, etc. for a column.
	Use when calculating total, avg, mean, median, etc. for a column in a CSV file.
	Example: 'sum sales by region', 'give the total sales by region', 'give total count of unit sold in sample.csv'
	:param file_path: Path to the csv file.
	:param group_by: Column name to group by. Use a comma-separated list for multiple columns.
	:param agg_column: Column name to aggregate.
	:param agg_function: Aggregation function to apply: sum, mean, median, min, max, std, count.
	:return: JSON string containing aggregation results and metadata
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

		# Read CSV with encoding fallback
		try:
			df = pd.read_csv(file_path_obj)
		except UnicodeDecodeError:
			df = pd.read_csv(file_path_obj, encoding="utf-8-sig")

		agg_function = agg_function.lower()
		group_columns = [col.strip() for col in group_by.split(",") if col.strip()]

		# Validate group_columns is not empty
		if not group_columns:
			return json.dumps(
				{"error": "No valid group by columns provided", "success": False}
			)

		# Validate input parameters
		missing_cols = [col for col in group_columns if col not in df.columns]
		if missing_cols:
			return json.dumps(
				{
					"error": f"Columns {missing_cols} not found in file '{file_path}'",
					"success": False,
				}
			)
		if agg_column not in df.columns:
			return json.dumps(
				{
					"error": f"Column '{agg_column}' not found in file '{file_path}'",
					"success": False,
				}
			)

		valid_agg_functions = ["sum", "mean", "median", "min", "max", "std", "count"]
		if agg_function not in valid_agg_functions:
			return json.dumps(
				{
					"error": f"Invalid aggregation function '{agg_function}'. Valid functions are: {', '.join(valid_agg_functions)}",
					"success": False,
				}
			)

		# Perform aggregation
		agg_result = (
			df.groupby(group_columns)[agg_column].agg(agg_function).reset_index()
		)

		# Add count of records per group
		group_counts = df.groupby(group_columns).size().reset_index(name="group_size")
		agg_result = agg_result.merge(group_counts, on=group_columns)

		# Calculate overall statistics
		overall_stats = {
			"total_records": len(df),
			"groups_count": len(agg_result),
			"overall_" + agg_function: float(df[agg_column].agg(agg_function)),
		}

		response = {
			"success": True,
			"file_info": {
				"path": str(file_path_obj),
				"size_bytes": file_path_obj.stat().st_size,
				"last_modified": pd.Timestamp(
					file_path_obj.stat().st_mtime, unit="s"
				).isoformat(),
				"total_rows": len(df),
				"total_columns": len(df.columns),
			},
			"aggregation": {
				"group_by": group_columns,
				"agg_function": agg_function,
				"agg_column": agg_column,
			},
			"results": {
				"grouped_data": agg_result.to_dict(orient="records"),
				"overall_statistics": overall_stats,
			},
			"metadata": {
				"timestamp": pd.Timestamp.now().isoformat(),
				"pandas_version": pd.__version__,
				"column_types": {
					agg_column: str(df[agg_column].dtype),
					**{col: str(df[col].dtype) for col in group_columns},
				},
			},
		}
		return json.dumps(response, default=serialize_number, indent=2)

	except Exception as e:
		return json.dumps(
			{
				"error": f"Error processing file '{file_path}': {str(e)}",
				"success": False,
				"exception_type": type(e).__name__,
			}
		)


if __name__ == "__main__":
	mcp.run()
