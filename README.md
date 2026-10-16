
# Parkwood Photo Web App v1

A browser-based version of the Parkwood stock photo processor.

## What it does

Upload multiple exterior stock photos in one go and process them as a batch.

The app:
- creates a conservative ground-edit mask
- previews the editable floor area
- sends each image to the OpenAI Images Edit API
- replaces/cleans only the forecourt area
- keeps the vehicle/background as protected as possible
- returns all finished images as a ZIP file

## Best use
This is intended for:
- Parkwood-style dealership exterior photos
- one car at a time
- 8–20 exterior photos per car

## Phone vs laptop

### On phone
Yes — once this app is deployed to a web host, you can use it from your phone in Safari/Chrome:
1. open the web address
2. upload all exterior photos
3. preview masks
4. process batch
5. download ZIP of edited images

### On laptop
You can also run it locally with Streamlit.

## Important limitation
This is still generative editing. The masking approach is designed to reduce drift, but you must always do a quick visual check before uploading stock to Auto Trader.

## Quick start — local
1. Install Python 3.11+
2. Open terminal in this folder
3. Create virtual environment and install requirements:
   - Windows:
     - `python -m venv .venv`
     - `.venv\Scripts\activate`
     - `pip install -r requirements.txt`
   - Mac/Linux:
     - `python3 -m venv .venv`
     - `source .venv/bin/activate`
     - `pip install -r requirements.txt`
4. Set your API key:
   - Windows PowerShell:
     - `$env:OPENAI_API_KEY="your_key_here"`
   - Mac/Linux:
     - `export OPENAI_API_KEY="your_key_here"`
5. Run:
   - `streamlit run app.py`
6. Open the local URL shown in the terminal

## Easiest ways to deploy for phone use
If you want to use this from your phone without touching code every time, deploy it to:
- Streamlit Community Cloud
- Render
- Railway

Then you just keep the web link bookmarked on your phone.

## Suggested deployment flow
- create a GitHub repo
- upload these files
- connect repo to Streamlit Community Cloud
- add `OPENAI_API_KEY` as a secret
- deploy
- open the generated URL on your phone

## Recommended batch process
1. Photograph one car
2. Select 12–15 exterior photos
3. Upload to the app
4. Preview masks
5. Adjust "Floor starts at" if needed
6. Process batch
7. Download edited ZIP
8. Flick through images
9. Upload to Auto Trader

## Files included
- `app.py` — Streamlit app
- `masking.py` — masking logic
- `editing.py` — OpenAI edit functions
- `prompt.txt` — Parkwood master edit prompt
- `requirements.txt`
- `config.json`
- `DEPLOYMENT_NOTES.md`
