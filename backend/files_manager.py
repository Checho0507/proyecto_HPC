import streamlit as st
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog
import os
import shutil

def select_vcf_file():
    # Crear una instancia de QApplication si no existe
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Abrir diálogo de selección de archivo
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(
        None, 
        "Seleccionar archivo VCF", 
        "", 
        "VCF Files (*.vcf)"
    )

    return file_path

def select_vcf_files():
    # Crear una instancia de QApplication si no existe
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Abrir diálogo de selección de archivos
    file_dialog = QFileDialog()
    file_paths, _ = file_dialog.getOpenFileNames(
        None, 
        "Seleccionar archivos VCF", 
        "", 
        "VCF Files (*.vcf)"
    )
    
    return file_paths

def copy_large_vcf_file(file_path):
    # Crear carpeta 'files' en el directorio raíz
    files_folder = os.path.join(os.path.dirname(__file__), 'files')
    os.makedirs(files_folder, exist_ok=True)
    
    if file_path.lower().endswith('.vcf'):
        # Nombre de archivo de destino
        destination_path = os.path.join(files_folder, os.path.basename(file_path))
        
        try:
            # Copiar archivo usando shutil (más eficiente para archivos grandes)
            shutil.copy2(file_path, destination_path)
            return destination_path  # Retornar la ruta del archivo copiado
        except Exception as e:
            st.error(f"Error al copiar {file_path}: {e}")
            return None
    else:
        st.warning("El archivo seleccionado no es un archivo VCF")
        return None

def parse_vcf(file_path):
    extracted_data = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('#'):
                continue  # Ignorar encabezados
            fields = line.strip().split('\t')
            chrom, pos, var_id, ref, alt, qual, filter_, info = fields[:8]
            format_ = fields[8] if len(fields) > 8 else None
            outputs = ','.join(fields[9:]) if len(fields) > 9 else None
            extracted_data.append({
                'chrom': chrom,
                'pos': int(pos),
                'id': var_id,
                'ref': ref,
                'alt': alt,
                'qual': qual,
                'filter': filter_,
                'info': info,
                'format': format_,
                'outputs': outputs
            })
    return extracted_data
