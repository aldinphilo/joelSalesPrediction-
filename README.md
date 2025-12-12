# SalesPrediction
Sales Prediction using AI

## Docker: dynamic model download

This project excludes the `Model/` directory from the image to keep the image small.
At container startup the image will attempt to create `/app/Model` by downloading a model source.

You can provide one of the following environment variables at `docker run`:

- `MODEL_URL` — a direct URL to a zip/tar or single-file containing the model artifacts.
- `MODEL_HF_ID` — a Hugging Face repo id (for example: `username/model-name`). If the model
	is private, also set `HF_HUB_TOKEN`.

Example `docker build` and `docker run` commands:

```powershell
docker build -t joel-sales-predictor:latest .

# Using a direct URL
docker run -e MODEL_URL="https://example.com/my-model.zip" -p 8000:8000 joel-sales-predictor:latest

# Or using a Hugging Face repo (private models require HF_HUB_TOKEN)
docker run -e MODEL_HF_ID="username/model-name" -e HF_HUB_TOKEN="<token>" -p 8000:8000 joel-sales-predictor:latest
```

The container's startup script (`/app/scripts/entrypoint.sh`) will run `/app/scripts/download_model.py`.
If the script finds an existing `/app/Model` directory it will skip the download.

