#!/usr/bin/env python3
"""
PDF Content Extraction using Microsoft Document Intelligence (Azure Form Recognizer)
This script extracts text content from PDF files using Azure's Document Intelligence service.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential


class PDFExtractor:
    """Handles PDF content extraction using Azure Document Intelligence"""
    
    def __init__(self):
        """Initialize the PDF extractor with Azure credentials from .env file"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Get credentials from environment variables
        self.endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        self.key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
        # Validate credentials
        if not self.endpoint or not self.key:
            raise ValueError(
                "Missing required environment variables. "
                "Please ensure AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and "
                "AZURE_DOCUMENT_INTELLIGENCE_KEY are set in your .env file."
            )
        
        # Initialize the Document Analysis Client
        self.client = DocumentAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )
        
    def extract_from_file(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract text content from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            output_path: Optional path to save the extracted text
            
        Returns:
            Extracted text content
        """
        # Validate input file
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError("Input file must be a PDF")
        
        print(f"📄 Processing PDF: {pdf_path}")
        
        # Read the PDF file
        with open(pdf_path, "rb") as f:
            poller = self.client.begin_analyze_document(
                "prebuilt-document", document=f
            )
        
        print("⏳ Analyzing document...")
        result = poller.result()
        
        # Extract text content
        extracted_text = []
        
        # Get content from pages
        for page in result.pages:
            print(f"📑 Processing page {page.page_number} of {len(result.pages)}")
            
            # Extract lines from the page
            for line in page.lines:
                extracted_text.append(line.content)
        
        # Join all text
        full_text = "\n".join(extracted_text)
        
        # Save to file if output path is provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(full_text)
            
            print(f"✅ Extracted text saved to: {output_path}")
        
        print(f"✅ Extraction complete! Total pages: {len(result.pages)}")
        print(f"📊 Total characters extracted: {len(full_text)}")
        
        return full_text
    
    def extract_structured_data(self, pdf_path: str) -> dict:
        """
        Extract structured data including tables, key-value pairs, etc.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing structured data
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"📄 Extracting structured data from: {pdf_path}")
        
        with open(pdf_path, "rb") as f:
            poller = self.client.begin_analyze_document(
                "prebuilt-document", document=f
            )
        
        result = poller.result()
        
        structured_data = {
            "pages": len(result.pages),
            "tables": [],
            "key_value_pairs": [],
            "paragraphs": []
        }
        
        # Extract tables
        if result.tables:
            print(f"📊 Found {len(result.tables)} table(s)")
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
            print(f"🔑 Found {len(result.key_value_pairs)} key-value pair(s)")
            for kv_pair in result.key_value_pairs:
                if kv_pair.key and kv_pair.value:
                    structured_data["key_value_pairs"].append({
                        "key": kv_pair.key.content,
                        "value": kv_pair.value.content
                    })
        
        # Extract paragraphs
        if result.paragraphs:
            print(f"📝 Found {len(result.paragraphs)} paragraph(s)")
            for para in result.paragraphs:
                structured_data["paragraphs"].append(para.content)
        
        return structured_data
    
    def format_as_markdown(self, pdf_path: str) -> str:
        """
        Extract content and format as markdown
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Markdown formatted content
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"📄 Extracting content as markdown from: {pdf_path}")
        
        with open(pdf_path, "rb") as f:
            poller = self.client.begin_analyze_document(
                "prebuilt-document", document=f
            )
        
        print("⏳ Analyzing document...")
        result = poller.result()
        
        markdown_content = []
        
        # Add document header
        pdf_name = Path(pdf_path).stem
        markdown_content.append(f"# {pdf_name}\n")
        markdown_content.append(f"*Extracted from PDF using Microsoft Document Intelligence*\n")
        markdown_content.append(f"*Total Pages: {len(result.pages)}*\n")
        markdown_content.append("---\n")
        
        # Process each page
        for page_num, page in enumerate(result.pages, 1):
            print(f"📑 Processing page {page_num} of {len(result.pages)}")
            
            markdown_content.append(f"\n## Page {page_num}\n")
            
            # Extract paragraphs if available
            page_paragraphs = [p for p in result.paragraphs if any(
                region.page_number == page_num for region in p.bounding_regions
            )] if result.paragraphs else []
            
            if page_paragraphs:
                for para in page_paragraphs:
                    markdown_content.append(f"{para.content}\n")
            else:
                # Fall back to lines if no paragraphs
                for line in page.lines:
                    markdown_content.append(f"{line.content}\n")
            
            markdown_content.append("\n")
        
        # Add tables section if tables exist
        if result.tables:
            markdown_content.append("\n---\n")
            markdown_content.append("\n## Tables\n")
            
            for idx, table in enumerate(result.tables, 1):
                markdown_content.append(f"\n### Table {idx}\n")
                markdown_content.append(self._format_table_as_markdown(table))
                markdown_content.append("\n")
        
        # Add key-value pairs section if they exist
        if result.key_value_pairs:
            markdown_content.append("\n---\n")
            markdown_content.append("\n## Extracted Fields\n")
            
            for kv_pair in result.key_value_pairs:
                if kv_pair.key and kv_pair.value:
                    key = kv_pair.key.content.strip()
                    value = kv_pair.value.content.strip()
                    markdown_content.append(f"- **{key}**: {value}\n")
        
        full_markdown = "".join(markdown_content)
        
        print(f"✅ Markdown formatting complete!")
        return full_markdown
    
    def _format_table_as_markdown(self, table) -> str:
        """
        Format a table as markdown
        
        Args:
            table: Azure Document Intelligence table object
            
        Returns:
            Markdown formatted table string
        """
        # Create a 2D array for the table
        grid = [['' for _ in range(table.column_count)] for _ in range(table.row_count)]
        
        # Fill the grid with cell contents
        for cell in table.cells:
            grid[cell.row_index][cell.column_index] = cell.content.strip()
        
        # Build markdown table
        markdown_lines = []
        
        # Add header row (first row)
        if table.row_count > 0:
            header = "| " + " | ".join(grid[0]) + " |"
            markdown_lines.append(header)
            
            # Add separator
            separator = "| " + " | ".join(['---'] * table.column_count) + " |"
            markdown_lines.append(separator)
            
            # Add data rows
            for row in grid[1:]:
                data_row = "| " + " | ".join(row) + " |"
                markdown_lines.append(data_row)
        
        return "\n".join(markdown_lines)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Extract content from PDF files using Microsoft Document Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract text from a PDF
  python extract_pdf.py input.pdf
  
  # Extract text and save to a file
  python extract_pdf.py input.pdf -o output.txt
  
  # Extract as markdown format
  python extract_pdf.py input.pdf --markdown -o output.md
  
  # Extract structured data (tables, key-value pairs)
  python extract_pdf.py input.pdf --structured
        """
    )
    
    parser.add_argument(
        "pdf_file",
        help="Path to the PDF file to process"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path for extracted text",
        default=None
    )
    
    parser.add_argument(
        "--structured",
        action="store_true",
        help="Extract structured data (tables, key-value pairs) instead of plain text"
    )
    
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Format output as markdown (with headings, tables, and formatting)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize extractor
        extractor = PDFExtractor()
        
        if args.markdown:
            # Extract and format as markdown
            markdown_text = extractor.format_as_markdown(args.pdf_file)
            
            # Save or display
            if args.output:
                output_file = Path(args.output)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(markdown_text)
                
                print(f"✅ Markdown content saved to: {args.output}")
            else:
                print("\n" + "="*50)
                print("MARKDOWN OUTPUT")
                print("="*50)
                print(markdown_text[:800] + "\n..." if len(markdown_text) > 800 else markdown_text)
        
        elif args.structured:
            # Extract structured data
            data = extractor.extract_structured_data(args.pdf_file)
            
            print("\n" + "="*50)
            print("STRUCTURED DATA SUMMARY")
            print("="*50)
            print(f"Total Pages: {data['pages']}")
            print(f"Tables: {len(data['tables'])}")
            print(f"Key-Value Pairs: {len(data['key_value_pairs'])}")
            print(f"Paragraphs: {len(data['paragraphs'])}")
            
            # Optionally save structured data
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n✅ Structured data saved to: {args.output}")
        else:
            # Extract plain text
            text = extractor.extract_from_file(args.pdf_file, args.output)
            
            # If no output file specified, print to console
            if not args.output:
                print("\n" + "="*50)
                print("EXTRACTED TEXT")
                print("="*50)
                print(text[:500] + "..." if len(text) > 500 else text)
        
        print("\n✨ Done!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
