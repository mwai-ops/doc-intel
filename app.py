#!/usr/bin/env python3
"""
Web UI for PDF Content Extraction using Microsoft Document Intelligence
"""

import os
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Progress tracking
progress_data = {}
progress_lock = threading.Lock()

# Initialize Azure Document Intelligence client
endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

if not endpoint or not key:
    raise ValueError("Missing Azure Document Intelligence credentials in .env file")

client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)


def update_progress(session_id, progress, status, time_remaining=None):
    """Update progress for a specific session"""
    with progress_lock:
        progress_data[session_id] = {
            'progress': progress,
            'status': status,
            'time_remaining': time_remaining,
            'timestamp': datetime.now().isoformat()
        }


def estimate_time_remaining(start_time, current_progress):
    """Estimate time remaining based on current progress"""
    if current_progress <= 0 or current_progress >= 100:
        return None
    
    elapsed = time.time() - start_time
    
    # Don't show estimate until we have at least 3 seconds of data
    if elapsed < 3:
        return None
    
    # Use exponential smoothing for more realistic estimates
    # Azure processing is non-linear, so we adjust the estimate
    if current_progress < 60:
        # Upload and analysis phase - slower
        estimated_total = (elapsed / current_progress) * 100 * 1.3
    else:
        # Extraction phase - faster
        estimated_total = (elapsed / current_progress) * 100
    
    remaining = estimated_total - elapsed
    return max(1, int(remaining))  # Never show 0 seconds


def extract_plain_text(pdf_path: str, session_id: str = None, start_time: float = None) -> str:
    """Extract plain text from PDF"""
    if session_id:
        update_progress(session_id, 0, "Starting...", None)
        time.sleep(0.3)
        update_progress(session_id, 5, "Preparing document...", None)
        time.sleep(0.5)
    
    with open(pdf_path, "rb") as f:
        if session_id:
            update_progress(session_id, 10, "Uploading to Azure AI...", None)
        poller = client.begin_analyze_document("prebuilt-document", document=f)
    
    # Simulate realistic progress during Azure processing
    if session_id:
        progress = 15
        last_update = time.time()
        
        while not poller.done():
            # Update progress every 0.5 seconds
            if time.time() - last_update >= 0.5:
                # Slow down as we approach 60%
                if progress < 40:
                    increment = 3
                elif progress < 55:
                    increment = 2
                else:
                    increment = 1
                
                progress = min(progress + increment, 60)
                time_remaining = estimate_time_remaining(start_time, progress) if start_time else None
                update_progress(session_id, progress, "Analyzing document with AI...", time_remaining)
                last_update = time.time()
            
            time.sleep(0.2)  # Check status frequently
        
        # Ensure we reach at least 60% before continuing
        if progress < 60:
            progress = 60
            time_remaining = estimate_time_remaining(start_time, progress) if start_time else None
            update_progress(session_id, progress, "Analysis complete...", time_remaining)
    
    result = poller.result()
    
    if session_id:
        time_remaining = estimate_time_remaining(start_time, 65) if start_time else None
        update_progress(session_id, 65, "Extracting text content...", time_remaining)
    
    extracted_text = []
    total_pages = len(result.pages)
    
    for idx, page in enumerate(result.pages):
        for line in page.lines:
            extracted_text.append(line.content)
        
        if session_id and total_pages > 0:
            page_progress = 70 + int((idx + 1) / total_pages * 25)
            time_remaining = estimate_time_remaining(start_time, page_progress) if start_time else None
            update_progress(session_id, page_progress, f"Extracting page {idx + 1}/{total_pages}...", time_remaining)
            time.sleep(0.1)  # Small delay to show progress per page
    
    return "\n".join(extracted_text)


def extract_structured_json(pdf_path: str, session_id: str = None, start_time: float = None) -> dict:
    """Extract structured data as JSON"""
    if session_id:
        update_progress(session_id, 0, "Starting...", None)
        time.sleep(0.3)
        update_progress(session_id, 5, "Preparing document...", None)
        time.sleep(0.5)
    
    with open(pdf_path, "rb") as f:
        if session_id:
            update_progress(session_id, 10, "Uploading to Azure AI...", None)
        poller = client.begin_analyze_document("prebuilt-document", document=f)
    
    # Realistic progress during Azure processing
    if session_id:
        progress = 15
        last_update = time.time()
        
        while not poller.done():
            if time.time() - last_update >= 0.5:
                if progress < 40:
                    increment = 3
                elif progress < 55:
                    increment = 2
                else:
                    increment = 1
                
                progress = min(progress + increment, 60)
                time_remaining = estimate_time_remaining(start_time, progress) if start_time else None
                update_progress(session_id, progress, "Analyzing document structure...", time_remaining)
                last_update = time.time()
            
            time.sleep(0.2)
        
        if progress < 60:
            progress = 60
            time_remaining = estimate_time_remaining(start_time, progress) if start_time else None
            update_progress(session_id, progress, "Analysis complete...", time_remaining)
    
    result = poller.result()
    
    if session_id:
        time_remaining = estimate_time_remaining(start_time, 50) if start_time else None
        update_progress(session_id, 50, "Extracting structured data...", time_remaining)
    
    structured_data = {
        "pages": len(result.pages),
        "tables": [],
        "key_value_pairs": [],
        "paragraphs": []
    }
    
    # Extract tables
    if result.tables:
        if session_id:
            update_progress(session_id, 60, "Extracting tables...")
        for table in result.tables:
            table_data = {
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": []
            }
            for cell in table.cells:
                table_data["cells"].append({
                    "row": cell.row_index,
                    "column": cell.column_index,
                    "content": cell.content
                })
            structured_data["tables"].append(table_data)
    
    # Extract key-value pairs
    if result.key_value_pairs:
        if session_id:
            update_progress(session_id, 75, "Extracting key-value pairs...")
        for kv_pair in result.key_value_pairs:
            if kv_pair.key and kv_pair.value:
                structured_data["key_value_pairs"].append({
                    "key": kv_pair.key.content,
                    "value": kv_pair.value.content
                })
    
    # Extract paragraphs
    if result.paragraphs:
        if session_id:
            update_progress(session_id, 85, "Extracting paragraphs...")
        for para in result.paragraphs:
            structured_data["paragraphs"].append(para.content)
    
    return structured_data


def format_table_as_markdown(table) -> str:
    """Format a table as markdown"""
    grid = [['' for _ in range(table.column_count)] for _ in range(table.row_count)]
    
    for cell in table.cells:
        grid[cell.row_index][cell.column_index] = cell.content.strip()
    
    markdown_lines = []
    
    if table.row_count > 0:
        header = "| " + " | ".join(grid[0]) + " |"
        markdown_lines.append(header)
        
        separator = "| " + " | ".join(['---'] * table.column_count) + " |"
        markdown_lines.append(separator)
        
        for row in grid[1:]:
            data_row = "| " + " | ".join(row) + " |"
            markdown_lines.append(data_row)
    
    return "\n".join(markdown_lines)


def extract_markdown(pdf_path: str, session_id: str = None, start_time: float = None) -> str:
    """Extract content and format as markdown"""
    if session_id:
        update_progress(session_id, 0, "Starting...", None)
        time.sleep(0.3)
        update_progress(session_id, 5, "Preparing document...", None)
        time.sleep(0.5)
    
    with open(pdf_path, "rb") as f:
        if session_id:
            update_progress(session_id, 10, "Uploading to Azure AI...", None)
        poller = client.begin_analyze_document("prebuilt-document", document=f)
    
    # Realistic progress during Azure processing
    if session_id:
        progress = 15
        last_update = time.time()
        
        while not poller.done():
            if time.time() - last_update >= 0.5:
                if progress < 35:
                    increment = 3
                elif progress < 45:
                    increment = 2
                else:
                    increment = 1
                
                progress = min(progress + increment, 50)
                time_remaining = estimate_time_remaining(start_time, progress) if start_time else None
                update_progress(session_id, progress, "Analyzing document...", time_remaining)
                last_update = time.time()
            
            time.sleep(0.2)
        
        if progress < 50:
            progress = 50
            time_remaining = estimate_time_remaining(start_time, progress) if start_time else None
            update_progress(session_id, progress, "Analysis complete...", time_remaining)
    
    result = poller.result()
    markdown_content = []
    
    # Add document header
    pdf_name = Path(pdf_path).stem
    markdown_content.append(f"# {pdf_name}\n")
    markdown_content.append(f"*Extracted from PDF using Microsoft Document Intelligence*\n")
    markdown_content.append(f"*Total Pages: {len(result.pages)}*\n")
    markdown_content.append("---\n")
    
    if session_id:
        update_progress(session_id, 50, "Formatting markdown...")
    
    # Process each page
    total_pages = len(result.pages)
    for page_num, page in enumerate(result.pages, 1):
        markdown_content.append(f"\n## Page {page_num}\n")
        
        # Extract paragraphs if available
        page_paragraphs = [p for p in result.paragraphs if any(
            region.page_number == page_num for region in p.bounding_regions
        )] if result.paragraphs else []
        
        if page_paragraphs:
            for para in page_paragraphs:
                markdown_content.append(f"{para.content}\n")
        else:
            for line in page.lines:
                markdown_content.append(f"{line.content}\n")
        
        markdown_content.append("\n")
        
        if session_id and total_pages > 0:
            page_progress = 55 + int((page_num / total_pages) * 25)
            time_remaining = estimate_time_remaining(start_time, page_progress) if start_time else None
            update_progress(session_id, page_progress, f"Formatting page {page_num}/{total_pages}...", time_remaining)
            time.sleep(0.1)
    
    # Add tables section
    if result.tables:
        if session_id:
            update_progress(session_id, 85, "Formatting tables...")
        markdown_content.append("\n---\n")
        markdown_content.append("\n## Tables\n")
        
        for idx, table in enumerate(result.tables, 1):
            markdown_content.append(f"\n### Table {idx}\n")
            markdown_content.append(format_table_as_markdown(table))
            markdown_content.append("\n")
    
    # Add key-value pairs section
    if result.key_value_pairs:
        if session_id:
            update_progress(session_id, 92, "Extracting fields...")
        markdown_content.append("\n---\n")
        markdown_content.append("\n## Extracted Fields\n")
        
        for kv_pair in result.key_value_pairs:
            if kv_pair.key and kv_pair.value:
                key = kv_pair.key.content.strip()
                value = kv_pair.value.content.strip()
                markdown_content.append(f"- **{key}**: {value}\n")
    
    return "".join(markdown_content)


@app.route('/')
def index():
    """Serve the main UI"""
    return render_template('index.html')


@app.route('/progress/<session_id>')
def progress_stream(session_id):
    """Stream progress updates via Server-Sent Events"""
    def generate():
        last_progress = -1
        while True:
            with progress_lock:
                data = progress_data.get(session_id)
            
            if data and data['progress'] != last_progress:
                last_progress = data['progress']
                yield f"data: {json.dumps(data)}\n\n"
                
                # End stream at 100%
                if data['progress'] >= 100:
                    break
            
            time.sleep(0.5)
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/extract', methods=['POST'])
def extract():
    """Handle PDF upload and extraction"""
    try:
        # Check if file was uploaded
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['pdf_file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        # Get selected formats and session ID
        formats = request.form.getlist('formats[]')
        session_id = request.form.get('session_id')
        
        if not formats:
            return jsonify({'error': 'No output format selected'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        start_time = time.time()
        
        # Initialize progress
        if session_id:
            update_progress(session_id, 5, "Starting extraction...")
        
        # Extract content in requested formats
        results = {}
        format_count = len(formats)
        
        for idx, fmt in enumerate(formats):
            base_progress = int((idx / format_count) * 95)
            
            if fmt == 'text':
                results['text'] = extract_plain_text(filepath, session_id, start_time)
            elif fmt == 'markdown':
                results['markdown'] = extract_markdown(filepath, session_id, start_time)
            elif fmt == 'json':
                results['json'] = extract_structured_json(filepath, session_id, start_time)
        
        # Complete
        if session_id:
            update_progress(session_id, 100, "Complete!")
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'results': results,
            'filename': filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

