import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from almuerzo.forms import ExcelUploadForm


def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)

        if form.is_valid():
            excel_file = request.FILES['excel_file']

            try:
                # Leer el archivo Excel
                if excel_file.name.endswith('.xlsx') or excel_file.name.endswith('.xls'):
                    # Usando pandas para leer el Excel
                    df = pd.read_excel(excel_file)

                    # Convertir DataFrame a lista de diccionarios
                    data = df.to_dict('records')

                    # Obtener nombres de columnas
                    columns = df.columns.tolist()

                    # Procesar los datos (aquí puedes hacer lo que necesites)
                    processed_data = process_excel_data(data)

                    messages.success(request, f'Archivo cargado exitosamente. {len(data)} registros encontrados.')

                    # Pasar los datos al template
                    return render(request, 'almuerzo/excel_result.html', {
                        'data': processed_data,
                        'columns': columns,
                        'row_count': len(data)
                    })

                else:
                    messages.error(request, 'Formato de archivo no soportado.')

            except Exception as e:
                messages.error(request, f'Error al leer el archivo: {str(e)}')

    else:
        form = ExcelUploadForm()

    return render(request, 'almuerzo/upload_excel.html', {'form': form})


def process_excel_data(data):
    """Función para procesar los datos del Excel"""
    processed_data = []

    for row in data:
        # Aquí puedes procesar cada fila según tus necesidades
        processed_row = {
            'original_data': row,
            'processed_info': f"Procesado: {len(row)} campos"
        }
        processed_data.append(processed_row)

    return processed_data
