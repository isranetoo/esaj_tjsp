import os
import PyPDF2
import re
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageFilter

def extract_patterns_from_pdf(file_path, page_index, patterns):
    """  """
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        if page_index >= len(reader.pages):
            print(f"Page {page_index} not found in {file_path}. Skipping...")
            return {key: None for key in patterns}
        
        page = reader.pages[page_index]  
        text = page.extract_text()
        
        results = {}
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                results[pattern_name] = match.group(1).strip()
            else:
                results[pattern_name] = None
        return results   

def save_pdf_cuts_as_images(pdf_path, page_index, cuts, output_folder):
    try:
        poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"  
        pages = convert_from_path(
            pdf_path, 
            first_page=page_index + 1, 
            last_page=page_index + 1,
            poppler_path=poppler_path
        )
        
        if not pages:
            print(f"Page {page_index} not found in {pdf_path}. Skipping...")
            return

        page = pages[0]
        for i, cut in enumerate(cuts):
            cropped_image = page.crop(cut)
            output_path = os.path.join(output_folder, f"{os.path.basename(pdf_path).replace('.pdf', '')}_cut_{i}.png")
            cropped_image.save(output_path)
            print(f"Saved cut {i} to {output_path}")
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")

def extract_text_from_images(img_path, lista_cortes_imagem):
    resultados = {}
    for i, coordenadas in enumerate(lista_cortes_imagem):
        image = Image.open(img_path)
        cropped_imagem = image.crop(coordenadas)
        
        
        enhanced_image = cropped_imagem.convert('L')  
        enhanced_image = enhanced_image.filter(ImageFilter.SHARPEN)
        enhanced_image = enhanced_image.point(lambda x: 0 if x < 128 else 255, '1')  

        
        custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
        result = pytesseract.image_to_string(
            enhanced_image,
            config=custom_config,
            lang='por'  
        )

        
        formatted_result = '\n'.join(
            line.strip() for line in result.splitlines() 
            if line.strip()
        )

        resultados[f"processo_{i}"] = formatted_result

    return resultados

patterns = {
    #POLO ATIVO
    "APELANTE": r'APELANTE:\s*(.+)',
    "APELANTES": r'APELANTES:\s*(.+)',
    #POLO PASSIVO
    "APELADO": r'APELADO:\s*(.+)',

    "AGRAVANTE": r'AGRAVANTE:\s*(.+)',
    #POLO PASSIVO
    "AGRAVADO": r'AGRAVADO:\s*(.+)',
    "AGRAVADA": r'AGRAVADA:\s*(.+)',

    #POLO ATIVO
    "EMBARGANTE": r'EMBARGANTE:\s*(.+)',
    #POLO PASSIVO
    "EMBARGADO": r'EMBARGADO:\s*(.+)',
    
    "R$": r'R\$\s*([\d\.,]+)',
    "Apelação Cível nº": r'Apelação Cível nº\s+(\d+)',
    "Apelação Criminal nº": r'Apelação Criminal nº\s+(\d+)',
}


folder_path = "./pdfs_folder"  
output_folder = "./output_images"

pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".pdf")]

page_index = 1 
cuts = [
    (0, 250, 1550, 724),
    (0, 250, 1650, 864),
    (0, 250, 1650, 690),  #left, top, right, bottom
    (0, 250, 1650, 724), 
]

if os.name == "nt":
    tesseract_path = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    if not os.path.exists(tesseract_path):
        raise FileNotFoundError(f"Tesseract executable not found at {tesseract_path}")

all_results = []
for pdf_file in pdf_files:
    results = extract_patterns_from_pdf(pdf_file, page_index, patterns)
    results["File"] = pdf_file
    all_results.append(results)
    save_pdf_cuts_as_images(pdf_file, page_index, cuts, output_folder)
    
    for i in range(len(cuts)):
        img_path = os.path.join(output_folder, f"{os.path.basename(pdf_file).replace('.pdf', '')}_cut_{i}.png")
        if os.path.exists(img_path):
            image_results = extract_text_from_images(img_path, cuts)
            results.update(image_results)

for result in all_results:
    print(f"\nResults for {result['File']}:")
    print("=" * 50)
    for key, value in result.items():
        if key != "File":
            if value:
                print(f"\n{key}:")
                print("-" * 30)
                print(value)
    print("=" * 50)
