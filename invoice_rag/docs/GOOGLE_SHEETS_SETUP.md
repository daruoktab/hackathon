# Google Sheets Integration Setup Guide

## Overview
This guide will help you set up Google Sheets API integration for the UrFinance Telegram Bot, allowing users to export their analysis directly to Google Sheets.

## Prerequisites
- Google Account
- Python environment with the bot installed

## Step-by-Step Setup

### 1. Install Required Libraries

```bash
pip install gspread oauth2client openpyxl pandas
```

### 2. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it "UrFinance Bot" or similar
4. Click "Create"

### 3. Enable Google Sheets API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"
4. Also enable "Google Drive API" (search and enable)

### 4. Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in:
   - **Service account name**: `urfinance-bot`
   - **Service account ID**: (auto-generated)
   - **Description**: "Service account for UrFinance bot to create spreadsheets"
4. Click "Create and Continue"
5. Skip the optional steps (click "Done")

### 5. Generate and Download Credentials

1. Click on the newly created service account email
2. Go to the "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON" format
5. Click "Create"
6. A JSON file will be downloaded automatically

### 6. Configure the Bot

1. Rename the downloaded JSON file to `google_credentials.json`
2. Move it to your project directory:
   ```
   e:\Github Project\hackathon\invoice_rag\google_credentials.json
   ```

3. **Important**: Add this file to `.gitignore` to keep credentials private:
   ```bash
   echo "google_credentials.json" >> .gitignore
   ```

### 7. Share Access (Optional)

If you want the created sheets to be accessible by specific users:

1. Copy the service account email from the credentials JSON file
   - Look for `"client_email"` in the JSON
   - Example: `urfinance-bot@project-id.iam.gserviceaccount.com`

2. When creating a sheet, the bot can share it with user emails programmatically

## Usage

### Excel Export (No Setup Required)
Users can export to Excel format without any Google setup:
```
/analysis → Click "📥 Export to Excel"
```

### Google Sheets Export
After setup, users can create live Google Sheets:
```
/analysis → Click "📊 Export to Google Sheets"
```

The bot will:
- Create a new Google Sheet
- Populate it with analysis data (Summary, Top Vendors, Weekly Breakdown)
- Return a shareable link

## Troubleshooting

### "Google Sheets integration is not configured"
- Ensure `google_credentials.json` exists in the `invoice_rag` folder
- Check file permissions

### "Libraries not installed"
```bash
pip install gspread oauth2client
```

### "Permission denied" when accessing sheet
- The sheet is owned by the service account
- Users need to request access OR
- Update code to share with specific emails:
  ```python
  spreadsheet.share('user@example.com', perm_type='user', role='writer')
  ```

### Rate Limits
Google Sheets API has quotas:
- 100 requests per 100 seconds per user
- 500 requests per 100 seconds per project

If you hit limits, implement caching or request throttling.

## Security Best Practices

1. ✅ **Never commit** `google_credentials.json` to Git
2. ✅ Add it to `.gitignore`
3. ✅ Use environment variables for sensitive data if needed
4. ✅ Restrict service account permissions to only Google Sheets/Drive
5. ✅ Regularly rotate credentials

## File Structure

```
invoice_rag/
├── google_credentials.json  # ← Place credentials here (gitignored)
├── telegram_bot/
│   └── bot.py               # Contains export functions
├── .gitignore               # Should include google_credentials.json
└── GOOGLE_SHEETS_SETUP.md   # This file
```

## Testing

Test the integration:
1. Start the bot: `python run_bot.py`
2. Send `/analysis` command
3. Click "📊 Export to Google Sheets"
4. Bot should respond with a Google Sheets link

## Support

If you encounter issues:
1. Check the bot logs for error messages
2. Verify credentials file exists and is valid JSON
3. Ensure APIs are enabled in Google Cloud Console
4. Check service account has proper permissions

---

**Setup Complete!** 🎉

Your users can now export their spending analysis to both Excel files and Google Sheets!
