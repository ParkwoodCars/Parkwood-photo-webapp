
# Deployment Notes

## Best option for you
For simple phone use, I'd deploy this with **Streamlit Community Cloud**.

### Why
- easiest setup
- gives you a link you can open on phone
- no app install
- mobile browser friendly

## Basic deployment
1. Create a GitHub account if needed.
2. Create a new repo, e.g. `parkwood-photo-webapp`.
3. Upload all files from this folder.
4. Go to Streamlit Community Cloud.
5. Connect your GitHub.
6. Select the repo.
7. Choose `app.py` as the entry file.
8. Add a secret/environment variable:
   - `OPENAI_API_KEY = your_api_key`
9. Deploy.

## Result
You get a URL like:
`https://parkwood-photo-webapp.streamlit.app`

Bookmark that on your phone.

## Notes
- phone uploads can be slower than laptop if you use many full-resolution images
- Wi-Fi is recommended
- 12–15 images per batch is sensible
- if an image is framed unusually low or high, adjust the floor slider before processing
