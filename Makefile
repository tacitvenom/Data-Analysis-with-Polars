.PHONY: setup-kernel notebook


setup-kernel:
	uv run python3 -m ipykernel install --user --name data_analysis_with_polars --display-name "data_analysis_with_polars"

notebook:
	uv run jupyter notebook
