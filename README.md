# PDF Content Extractor using Microsoft Document Intelligence

A powerful Web Application to extract text and structured data from PDF files using Azure's Document Intelligence service.

## Features

- 📄 **Smart PDF Extraction** - Extract plain text, structured data, and markdown from any PDF
- 🌐 **Modern Web Interface** - Beautiful, dark-mode UI with drag & drop support
- ⚡ **Real-time Progress** - Watch the extraction process with detailed step-by-step progress tracking
- 📝 **Markdown Formatting** - Get perfect markdown output with headers, tables, and lists preserved
- 📊 **Structured Data** - Extract tables and key-value pairs into JSON format
- 👁️ **Interactive Viewer** - View results directly in the browser with one-click copy
- 💾 **Multi-format Export** - Download results in Text, Markdown, or JSON formats
- 🔐 **Secure** - API keys managed safely via environment variables

## Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy your `.env` file from your other project or create a new one:

```bash
# Copy .env.example to .env
copy .env.example .env
```

Edit the `.env` file and add your Azure Document Intelligence credentials:

```env
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-api-key-here
```

**Where to find these values:**
- Log in to [Azure Portal](https://portal.azure.com)
- Navigate to your Document Intelligence resource
- Go to "Keys and Endpoint" section
- Copy the endpoint URL and one of the keys

## Usage

1. Start the web server:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to `http://localhost:5000`
3. **Drag & Drop** your PDF file into the upload zone
4. **Select Output Formats**:
   - **Plain Text**: Extract raw text content.
   - **Markdown**: Get formatted text with headers and tables.
   - **JSON**: Get structured data including tables and key-value pairs.
5. Click **Extract Content** and watch the real-time progress
6. View results in the interactive viewer or copy them to your clipboard

## Troubleshooting

### Missing Environment Variables
If you see an error about missing environment variables, ensure:
1. Your `.env` file exists in the project root
2. It contains both `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` and `AZURE_DOCUMENT_INTELLIGENCE_KEY`
3. The values are correct (no extra spaces or quotes)

### Authentication Errors
- Verify your API key is correct
- Ensure your endpoint URL is properly formatted
- Check that your Azure resource is active and not expired

### File Not Found
- Ensure the PDF file path is correct
- Use absolute paths if relative paths don't work
- Check file permissions

## Requirements

- Python 3.7+
- Azure Document Intelligence resource (with API key and endpoint)
- Internet connection for API calls

## Dependencies

- `azure-ai-formrecognizer==3.3.3` - Azure Document Intelligence SDK
- `python-dotenv==1.0.0` - Environment variable management
- `Flask` - Web Framework

## License

This project is provided as-is for educational and development purposes.
