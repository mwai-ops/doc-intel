# PDF Content Extractor using Microsoft Document Intelligence

A Python CLI tool to extract text and structured data from PDF files using Azure's Document Intelligence service (formerly Form Recognizer).

## Features

- 📄 Extract plain text from PDF files
- 🌐 **Web Interface** - User-friendly web UI for easy uploading and extraction
- 📝 **Extract and format as Markdown** - Get beautifully formatted markdown with headings, tables, and proper structure
- 📊 Extract structured data (tables, key-value pairs, paragraphs)
- 💾 Save extracted content to files
- 🔐 Secure credential management using `.env` files
- 🎯 Simple command-line interface

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

### Web Interface

1. Start the web server:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to `http://localhost:5000`
3. Upload a PDF file and select your desired output formats (Text, Markdown, JSON)
4. View the results directly in the browser or download the extracted files

### Basic Text Extraction

Extract text from a PDF and display it:

```bash
python extract_pdf.py path/to/your/document.pdf
```

### Save Extracted Text to File

```bash
python extract_pdf.py input.pdf -o output.txt
```

### Extract as Markdown Format

Extract with proper markdown formatting including headings, tables, and structure:

```bash
python extract_pdf.py document.pdf --markdown -o output.md
```

This will create a markdown file with:
- Document title and metadata  
- Page-by-page content with headings
- Tables formatted as markdown tables
- Key-value pairs formatted as bullet lists

### Extract Structured Data

Extract tables, key-value pairs, and paragraphs:

```bash
python extract_pdf.py document.pdf --structured
```

### Save Structured Data as JSON

```bash
python extract_pdf.py document.pdf --structured -o output.json
```

## Command Line Options

```
positional arguments:
  pdf_file              Path to the PDF file to process

optional arguments:
  -h, --help           Show help message and exit
  -o, --output OUTPUT  Output file path for extracted text
  --markdown           Format output as markdown (with headings, tables, and formatting)
  --structured         Extract structured data (tables, key-value pairs)
```

## Example Output

### Plain Text Extraction
```
📄 Processing PDF: sample.pdf
⏳ Analyzing document...
📑 Processing page 1 of 3
📑 Processing page 2 of 3
📑 Processing page 3 of 3
✅ Extraction complete! Total pages: 3
📊 Total characters extracted: 5432
```

### Structured Data Extraction
```
📄 Extracting structured data from: invoice.pdf
📊 Found 2 table(s)
🔑 Found 15 key-value pair(s)
📝 Found 8 paragraph(s)

==================================================
STRUCTURED DATA SUMMARY
==================================================
Total Pages: 2
Tables: 2
Key-Value Pairs: 15
Paragraphs: 8
```

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

## License

This project is provided as-is for educational and development purposes.
