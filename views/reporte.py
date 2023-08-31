from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from app.edificaciones.layer.application.ambiente_app_service import AmbienteAppService
from app.edificaciones.models import (AmbienteRecurso,AmbienteUso, Bloque,Dependencia,UsoTipo,Subambiente, AmbienteItem, RecursoItem)
import app.edificaciones.utils.excel as excel
from django.db.models import Max
import json
from django.shortcuts import render

# from app.edificaciones.layer.application.ambiente_app_service import AmbienteAppService

@login_required
@require_http_methods(["GET"])
def ambiente_xls_detallado(request):
    data = request.GET.get('data')
    data_dict = json.loads(data)

    selectores = data_dict.get('selectores')

    ambientesUsos = AmbienteUso.objects.all()
    
    if selectores:
        campus_id = selectores.get('campus_id')
        bloque_id = selectores.get('bloque_id')
        numero_piso = selectores.get('numero_piso')
        dependencia_id = selectores.get('dependencia_id')
        año_id = selectores.get('año_id')
        ambientesUsos = AmbienteAppService.get_ambiente_usos_filtrados(campus_id, bloque_id, numero_piso, dependencia_id, año_id)
    
    # col_width = 19*256  # Valor en unidades de 1/20 de punto
    # hoja.col(0).width = col_width  # Establecer la altura de la fila
    excel_doc = excel.ExcelDocument()

    # Agregar una nueva hoja al documento
    sheet = excel_doc.add_sheet("Reporte")

    # Crear una instancia de la hoja
    excel_sheet = excel.ExcelSheet(sheet)

    title, subtitle, institution_title = "UNIVERSIDAD NACIONAL DE LOJA", "DIRECCIÓN DE DESARROLLO FÍSICO", "INFRAESTRUCTURA DE LA FACULTAD DE LA EDUCACIÓN EL ARTE Y LA COMUNICACIÓN"

    excel_sheet.insert_title_subtitle(title, subtitle, institution_title)

    #ajuste de altura de filas
    row_dimensions = [19, 34, 46, 36, 42, 136]
    for row, height in zip([1, 2, 3, 9, 10, 11, 12, 13], row_dimensions):
        excel_sheet.set_row_dimensions(row=row, height=height)



    # Verificar si existe un AmbienteUso relacionado con el recurso con el código deseado
    existe_recurso = False


    #region Inicio Encabezados
    # Definir encabezados no dinamicos de nro. a disponibilidad codigo puerta
    headers = [
        {
            "start_row": 9,
            "end_row": 13,
            "start_col": i,
            "end_col": i,
            "width": [10, 30, 60, 30, 30, 30][i],
            "text": label,
        }
        for i, label in enumerate(
            [
                "NRO.",
                "VERIFICADOR DE INFORMACIÓN A AGOSTO DEL 2020(según filtro de consulta)",
                "UBICACIÓN ZONA",
                "FACULTAD",
                "CÓDIGO ANTERIOR",
                "DISPONIBILIDAD DEL CÓDIGO SOBRE PUERTA",
            ]
        )
    ]
    excel_sheet.insert_table_headers(headers=headers)

    #contendrá el valor máximo de la cantidad de subambientes entre todos los objetos  AmbienteUso.
    max_subambientes = AmbienteUso.objects.annotate(num_subambientes=Max('subambientes__codigo')).aggregate(Max('num_subambientes'))['num_subambientes__max']

    # Calcular el rango de columnas de los encabezados dinámicos
    start_col_dynamic = 10
    end_col_dynamic = start_col_dynamic + max_subambientes - 1

    
    # Insertar encabezados no dinamicos de codigo propuesto
    # 4 encabezados fijos 
    fixed_headers = [
        {
            "start_row": 10,
            "end_row": 13,
            "start_col": 6,
            "end_col": 6,
            "rotation": 90,
            "width": 6,
            "text": "CAMPUS",
        },
        {
            "start_row": 10,
            "end_row": 13,
            "start_col": 7,
            "end_col": 7,
            "rotation": 90,
            "width": 6,
            "text": "BLOQUE",
        },
        {
            "start_row": 10,
            "end_row": 13,
            "start_col": 8,
            "end_col": 8,
            "rotation": 90,
            "width": 6,
            "text": "PISO",
        },
        {
            "start_row": 10,
            "end_row": 13,
            "start_col": 9,
            "end_col": 9,
            "rotation": 90,
            "width": 6,
            "text": "AMBIENTE",
        },
    ]

    # Crear los encabezados dinámicos (cambia esta lista según tus necesidades)
    dynamic_headers = [
        {
            "start_row": 10,
            "end_row": 13,
            "start_col": 10 + i,
            "end_col": 10 + i,
            "rotation": 90,
            "width": 6,
            "text": f"SUBAMBIENTE {i+1}",
        }
        for i in range(max_subambientes)
    ]

    # Crear el encabezado fijo adicional
    additional_fixed_header = {
        "start_row": 10,
        "end_row": 13,
        "start_col":  end_col_dynamic + 1,
        "end_col": end_col_dynamic + 1,
        "rotation": 0,
        "width": 25,
        "text": "CÓDIGO PROPUESTO FINAL",
    }

    # Se combinan todos encabezados
    all_headers = fixed_headers + dynamic_headers + [additional_fixed_header]

    # Crear el grupo de encabezados completo
    headers_group = [
        {
            "title_group": "CÓDIGO PROPUESTO",
            "start_row_group": 9,
            "end_row_group": 9,
            "start_col_group": 6,
            "end_col_group": end_col_dynamic + 1,
            "color": 22,
            "childrens": all_headers,
        }
    ]

    # Insertar los encabezados en la hoja de cálculo
    excel_sheet.insert_table_headers_group(headers_group=headers_group)

    #columnas recomendaciones y usos 
    headers = [
        {
            "start_row": 9,
            "end_row": 13,
            "start_col": excel_sheet.get_next_col(),
            "end_col": excel_sheet.add_current_col(),
            "width": 30,
            "color": 22,
            "text": text,
        }
        for text in [
            "RECOMENDACIONES DEL AMBIENTE VERIFICADO POR DESARROLLO FISCO AL 2019(fecha del uso anterior)",
            "USO DEL AMBIENTE VERIFICADO POR DESARROLLO FISCO AL 2019 (fecha del uso anterior)",
            "USO DEL AMBIENTE VERIFICADO POR DESARROLLO FÍSICO Y CLASIFICADO DE ACUERDO A TABLA DE CATEGORÍAS",
        ]
    ]
    excel_sheet.insert_table_headers(headers=headers)

    #columna dimensiones del ambiente
    headers_group = [
        {
            "title_group": "DIMENSIONES DEL AMBIENTE",
            "start_row_group": 9,
            "end_row_group": 9,
            "start_col_group": excel_sheet.get_next_col(),
            "end_col_group": excel_sheet.get_next_col() + 2,
            "color": 22,
            "childrens": [
                {
                    "start_row": 10,
                    "end_row": 10,
                    "start_col": excel_sheet.get_next_col(),
                    "end_col": excel_sheet.get_next_col(),
                    "width": 6,
                    "text": "L",
                },
                {
                    "start_row": 11,
                    "end_row": 13,
                    "start_col": excel_sheet.get_next_col(),
                    "end_col": excel_sheet.add_current_col(),
                    "rotation": 90,
                    "text": "LARGO O FONDO DEL AULA O AMBIENTE EN METROS",
                },
                {
                    "start_row": 10,
                    "end_row": 10,
                    "start_col": excel_sheet.get_next_col(),
                    "end_col": excel_sheet.get_next_col(),
                    "width": 6,
                    "text": "A",
                },
                {
                    "start_row": 11,
                    "end_row": 13,
                    "start_col": excel_sheet.get_next_col(),
                    "end_col": excel_sheet.add_current_col(),
                    "rotation": 90,
                    "text": "ANCHO DEL AMBIENTE O AULA EN DIRECCIÓN DE LA PIZARRA EN METROS",
                },
                {
                    "start_row": 10,
                    "end_row": 10,
                    "start_col": excel_sheet.get_next_col(),
                    "end_col": excel_sheet.get_next_col(),
                    "width": 6,
                    "text": "H",
                },
                {
                    "start_row": 11,
                    "end_row": 13,
                    "start_col": excel_sheet.get_next_col(),
                    "end_col": excel_sheet.add_current_col(),
                    "rotation": 90,
                    "text": "ALTURA DEL PISO A CIELO RASO",
                },
            ],
        },
    ]
    excel_sheet.insert_table_headers_group(headers_group=headers_group)


    textos_orden = [
            "ACCESO A LAS PERSONAS CON CAPACIDAD REDUCIDA",
            "ESTADO DE PAREDES",
            "MATERIAL DE CIELO RASO",
            "ESTADO DE CIELO RASO",
            "MATERIAL DE PISO",
            "ESTADO DE PISO",
            "DISEÑO DE PERSIANAS Y CORTINAS",
            "ESTADO DE PERSIANAS O CORTINAS EN VENTANAS",
            "MATERIAL DE LA PUERTA",
            "TIPO APERTURA DE LA PUERTA",
            "TIPO DE SEGURIDAD DE LA PUERTA",
            "ESTADO EN GENERAL DE PUERTA",
            "MATERIAL DE VENTANAS",
            "ESTADO DE VENTANAS",
            "TIPO DE VENTILACIÓN",
            "CAPACIDAD DE VENTILACIÓN",
            "TIPO DE LUMINARIA",
            "NRO LUMINARIAS",
            "NRO FOCOS O TUBOS EN CADA LUMINARIA",
            "LONGITUD DE LAMPARAS SI FLUORESCENTES",
            "NRO DE TUBOS O FOCOS SIN FUNCIONAR",
            "OBSERVACIONES DEL ESTADO DE LAS LUMINARIAS",
            "TIPO DE CONEXIÓN A INTERNET",
            "TIPO",
            "DISPONIBILIDAD DE PANTALLA",
            "SEGURIDAD DE EQUIPOS",
            "NRO DE DOBLES",
            "POR REPARAR",
        ]
    
    existe_ambienteUso_con_recurso_item_recursoId = AmbienteItem.objects.filter(recurso_item__recurso_id=1).exists()
    if existe_ambienteUso_con_recurso_item_recursoId:
    
        #columna caracteristicas basicas del ambiente
        DeAmbienteItem_orden = []
        for orden in range(1, 12):
            texto = textos_orden[orden - 1]
            if AmbienteItem.objects.filter(recurso_item__orden=orden).exists():
                DeAmbienteItem_orden.append(texto)


        if DeAmbienteItem_orden:
            headers_group = [
                {
                    "title_group": "CARACTERÍSTICAS BÁSICAS DEL AMBIENTE",
                    "start_row_group": 9,
                    "end_row_group": 9,
                    "start_col_group": excel_sheet.get_next_col(),
                    "end_col_group": excel_sheet.get_next_col() + len(DeAmbienteItem_orden) - 1,
                    "color": 22,
                    "childrens": [
                        {
                            "start_row": 10,
                            "end_row": 13,
                            "start_col": excel_sheet.get_next_col(),
                            "end_col": excel_sheet.add_current_col(),
                            "rotation": 90,
                            "text": text,
                        }
                        for text in DeAmbienteItem_orden
                    ],
                }
            ]
            excel_sheet.insert_table_headers_group(headers_group=headers_group)
                    
    existe_ambienteUso_con_recurso_item_recursoId = AmbienteItem.objects.filter(recurso_item__recurso_id=2).exists()
    if existe_ambienteUso_con_recurso_item_recursoId:    
        #columna iluminacion natural y ventilacion
        DeAmbienteItem_orden = []
        for orden in range(13, 16):
            texto = textos_orden[orden - 1]
            if AmbienteItem.objects.filter(recurso_item__orden=orden).exists():
                DeAmbienteItem_orden.append(texto)

        if DeAmbienteItem_orden:
            headers_group = [
                {
                    "title_group": "ILUMINACIÓN NATURAL Y VENTILACIÓN",
                    "start_row_group": 9,
                    "end_row_group": 9,
                    "start_col_group": excel_sheet.get_next_col(),
                    "end_col_group": excel_sheet.get_next_col() + len(DeAmbienteItem_orden) - 1,
                    "color": 22,
                    "childrens": [
                        {
                            "start_row": 10,
                            "end_row": 13,
                            "start_col": excel_sheet.get_next_col(),
                            "end_col": excel_sheet.add_current_col(),
                            "rotation": 90,
                            "text": text,
                        }
                        for text in DeAmbienteItem_orden
                    ],
                }
            ]
            excel_sheet.insert_table_headers_group(headers_group=headers_group)
    
    existe_ambienteUso_con_recurso_item_recursoId = AmbienteItem.objects.filter(recurso_item__recurso_id=3).exists()
    if existe_ambienteUso_con_recurso_item_recursoId:
        #columna iluminacion artificial
        DeAmbienteItem_orden = []
        for orden in range(17, 22):
            texto = textos_orden[orden - 1]
            if AmbienteItem.objects.filter(recurso_item__orden=orden).exists():
                DeAmbienteItem_orden.append(texto)

        if DeAmbienteItem_orden:
            headers_group = [
                {
                    "title_group": "ILUMINACIÓN ARTIFICIAL",
                    "start_row_group": 9,
                    "end_row_group": 9,
                    "start_col_group": excel_sheet.get_next_col(),
                    "end_col_group": excel_sheet.get_next_col() + len(DeAmbienteItem_orden) - 1,
                    "color": 22,
                    "childrens": [
                        {
                            "start_row": 10,
                            "end_row": 13,
                            "start_col": excel_sheet.get_next_col(),
                            "end_col": excel_sheet.add_current_col(),
                            "rotation": 90,
                            "text": text,
                        }
                        for text in DeAmbienteItem_orden
                    ],
                }
            ]
            excel_sheet.insert_table_headers_group(headers_group=headers_group)
    
    existe_ambienteUso_con_recurso_item_recursoId = AmbienteItem.objects.filter(recurso_item__recurso_id=4).exists()
    if existe_ambienteUso_con_recurso_item_recursoId:
        
        #columna facilidades para utilizar recursos multimedia
        
        DeAmbienteItem_orden = []
        for orden in range(23, 28):
            texto = textos_orden[orden - 1]
            if AmbienteItem.objects.filter(recurso_item__orden=orden).exists():
                DeAmbienteItem_orden.append(texto)

        if DeAmbienteItem_orden:

            headers_group = [
                {
                    "title_group": "FACILIDADES PARA UTILIZAR RECURSOS MULTIMEDIA",
                    "start_row_group": 9,
                    "end_row_group": 9,
                    "start_col_group": excel_sheet.get_next_col(),
                    "end_col_group": excel_sheet.get_next_col() + len(DeAmbienteItem_orden) - 1,
                    "color": 22,
                    "childrens": [
                        {
                            "start_row": 10,
                            "end_row": 13,
                            "start_col": excel_sheet.get_next_col(),
                            "end_col": excel_sheet.add_current_col(),
                            "rotation": 90,
                            "text": text,
                        }
                        for text in DeAmbienteItem_orden
                    ],
                }
            ]
            excel_sheet.insert_table_headers_group(headers_group=headers_group)

    #columna de observacion general
    headers = [
        {
            "start_row": 9,
            "end_row": 13,
            "start_col": excel_sheet.get_next_col(),
            "end_col": excel_sheet.add_current_col(),
            "width": 46,
            "text": "OBSERVACIÓN GENERAL",
        },
    ]
    excel_sheet.insert_table_headers(headers=headers)

    #columna area del ambiente
    headers_group = [
        {
            "title_group": "Aa",
            "start_row_group": 9,
            "end_row_group": 9,
            "start_col_group": excel_sheet.get_next_col(),
            "end_col_group": excel_sheet.get_next_col(),
            "childrens": [
                {
                    "start_row": 10,
                    "end_row": 13,
                    "start_col": excel_sheet.get_next_col(),
                    "end_col": excel_sheet.add_current_col(),
                    "width": 20,
                    "text": "ÁREA DEL AMBIENTE",
                },
            ],
        }
    ]
    excel_sheet.insert_table_headers_group(headers_group=headers_group)

    #columna capacidad teorica de alumnos
    headers_group = [
        {
            "title_group": "CA",
            "start_row_group": 9,
            "end_row_group": 9,
            "start_col_group": excel_sheet.get_next_col(),
            "end_col_group": excel_sheet.get_next_col(),
            "childrens": [
                {
                    "start_row": 10,
                    "end_row": 13,
                    "start_col": excel_sheet.get_next_col(),
                    "end_col": excel_sheet.add_current_col(),
                    "width": 20,
                    "text": "CAPACIDAD TEÓRICA DE ALUMNOS PARA AULAS CA=(L-Z) * A / AS",
                },
            ],
        },
    ]
    excel_sheet.insert_table_headers_group(headers_group=headers_group)
    #endregion
    #fin region encabezados

    #region Inicio filas
    
    #'ambienteUs__subambientes',
    #'ambienteUs__recursos__items'

    # Diccionario vacio para almacenar el recuento de recursos
    recurso_counts = {}
    # Diccionario vacio para almacenar el recuento de subambientes
    subambiente_counts = [] # Crear una lista para contar los subambientes

    for a, ambienteU in enumerate(ambientesUsos):
        excel_sheet.write_column_data(row=14 + a, column=0, data=a + 1) #nro
        excel_sheet.write_column_data(row=14 + a, column=1, data=str(ambienteU.usuario))#verificador
        excel_sheet.write_column_data(
            row=14 + a, column=2, data=ambienteU.ambiente.bloque.campus.nombre #ubicacion zona
        )
        excel_sheet.write_column_data(
            row=14 + a, column=3, data=ambienteU.dependencia.nombre #facultad
        )
        excel_sheet.write_column_data(
            row=14 + a, column=4, data=ambienteU.codigo_anterior #codigo anterior
        )
        
        puerta_disponibilidad = "Sí" if ambienteU.codigo_puerta else "No" #disponibilidad en puerta
        excel_sheet.write_column_data(
            row=14 + a, column=5, data=puerta_disponibilidad
        )

        excel_sheet.write_column_data(
            row=14 + a, column=6, data=ambienteU.ambiente.bloque.campus.codigo #codigo de campus
        )

        excel_sheet.write_column_data(
            row=14 + a, column=7, data=ambienteU.ambiente.bloque.numero #numero de bloque
        )
        excel_sheet.write_column_data(
            row=14 + a, column=8, data=ambienteU.ambiente.numero_piso #numero de piso
        )

        excel_sheet.write_column_data(
            row=14 + a, column=9, data=ambienteU.ambiente.pk #numero de ambiente
        )

        subambiente_list = set()  # Crear un conjunto para almacenar los nombres de subambientes únicos

        for i, subambiente in enumerate(ambienteU.subambientes.all()):
            excel_sheet.write_column_data(
                row=14 + a,
                column=10 + i,  # Sumamos 3 para desplazar a las columnas siguientes
                data=subambiente.codigo  # Código del subambiente
            )

        excel_sheet.write_column_data(
            row=14 + a, column=end_col_dynamic + 1, data=ambienteU.codigo_display #codigo propuesto final 
        )

        excel_sheet.write_column_data(
            row=14 + a, column=end_col_dynamic + 2, data=ambienteU.observacion #observacion
        )

        if ambienteU.ambiente_uso is not None: # uso tipo anterior
            excel_sheet.write_column_data(
                row=14 + a,
                column=end_col_dynamic + 3,
                data=ambienteU.ambiente_uso.uso_tipo.nombre  
            )
        else:
            # Manejar el caso donde ambienteU.ambiente_uso es None
            # Puedes decidir si quieres poner algún valor predeterminado o simplemente dejarlo en blanco.
            excel_sheet.write_column_data(
                row=14 + a,
                column=end_col_dynamic + 3,
                data="No hay datos de verificación"  # Dejar en blanco o usar algún valor predeterminado
            )

        excel_sheet.write_column_data(
            row=14 + a, column=end_col_dynamic + 4, data=ambienteU.uso_tipo.nombre #uso tipo 
        )

        excel_sheet.write_column_data(
            row=14 + a, column=end_col_dynamic + 5, data=ambienteU.largo #Largo
        )
        excel_sheet.write_column_data(
            row=14 + a, column=end_col_dynamic + 6, data=ambienteU.ancho #Ancho
        )
        excel_sheet.write_column_data(
            row=14 + a, column=end_col_dynamic + 7, data=ambienteU.alto #Altura
        )

        cont = 0
        #columnas dinamicas de recursos e itemRecursos
        for ambiente_recurso in ambienteU.recursos.all():
            nombre_recurso = ambiente_recurso.recurso.nombre

            if nombre_recurso not in recurso_counts:
                recurso_counts[nombre_recurso] = []

            for ambiente_item in ambiente_recurso.items.all():
                nombre_recurso_item = ambiente_item.recurso_item.nombre
                excel_sheet.write_column_data(
                    row=14 + a,
                    column=21 + len(subambiente_counts) + cont,
                    data=ambiente_item.valor if ambiente_item.valor else "",
                )
                
                cont += 1

                if nombre_recurso_item not in recurso_counts[nombre_recurso]:
                    recurso_counts[nombre_recurso].append(nombre_recurso_item)

        
        excel_sheet.write_column_data(
            row=14 + a, column=21 + len(subambiente_counts) + cont , data=ambienteU.observacion #Observación
        )
        excel_sheet.write_column_data(
            row=14 + a, column=21 + len(subambiente_counts) + cont + 1, data=ambienteU.area #area
        )
        
        excel_sheet.write_column_data(row=14 + a, column=21 + len(subambiente_counts) + cont + 2, # numero de alumnos
                                        data=f"{ambienteU.aula.capacidad_alumnos if ambienteU.aula is not None else '0'} alumnos")

    #endregion filas

    #Se crea una instancia de  HttpResponse que se utilizará para enviar el archivo Excel al navegador del usuario. 
    response = HttpResponse(content_type="application/ms-excel")
    # se indica al navegador que debe descargar el contenido como un archivo adjunto con el nombre de archivo  "reporte_excel.xls". 
    response["Content-Disposition"] = 'attachment; filename="reporte_excel.xls"'

    # libro.save(response)
    excel_doc.save(response)

    return response
