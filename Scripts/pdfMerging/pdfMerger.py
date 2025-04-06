from pypdf import PdfMerger
import os

# Get all PDF files in the current directory
pdfs = [f for f in os.listdir() if f.endswith('.pdf')]

merger = PdfMerger()

for pdf in pdfs:
    # Open each PDF and append it to the merger
    with open(pdf, 'rb') as pdf_file:
        merger.append(pdf_file)

# Write out the merged PDF and close the merger
merger.write("result.pdf")
merger.close()
