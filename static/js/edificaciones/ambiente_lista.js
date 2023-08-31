$(function () {
    initDataTable();
});

function initDataTable() {
    table = $('#tabla-ambientes').DataTable({
        
        "processing": true,
        "serverSide": true,
        "stateSave": true,
        "order": [[0, "asc"]],
        "ajax": {
            "url": url_ambiente_lista,
            "type": "GET",
            "data": function (d) {
                d.campus_id = $('#filtro_campus').val();
                d.bloque_id = $('#filtro_bloque').val();
                d.numero_piso = $('#filtro_numero_piso').val();
                d.dependencia_id = $('#filtro_dependencia').val();
                d.año_id = $('#filtro_año').val();
            },
            "error": function (err) {
                // sesión caducada
                if (err.status == 401){
                    alert_notificacion('Error', err.responseJSON.detail, 'error').then((result) => {
                         window.location = window.location;
                    });
                }else{
                    mensaje_error(err.responseJSON.detail);
                }
            }
        },
        "columns": [
            {"data": "descripcion"},
            {"data": "ubicacion"},
            {"data": "codigo_actual"},
            {"data": "dependencia_actual"},
            {"data": "revision_anio_actual"},
        ],
         "columnDefs": [
            {
                orderable: false,
                targets: [1],
            },
            {targets: [0], render: function (data, type, row) {
                return '<a href="'+ url_ambiente_detalle + row.id +'">'+ data + '</a>';
            }},
        ],
        "language": {"url": "/static/plugins/datatables/es.js"}
    });

    $('#filtro_campus').change(function (e) {
        campus_get_bloques($(this).val(), "#filtro_bloque");
        $('#filtro_bloque').val('').change();
    });

    $('#filtro_bloque').change(function (e) {
        bloque_get_pisos($(this).val(), "#filtro_numero_piso");
        $('#filtro_numero_piso').val('').change();
    });
    
    $('#filtro_numero_piso, #filtro_dependencia, #filtro_año').change(function (e) {
        table.draw();
    });


    
}

// modal crear/editar requisito, detectar cuando se abre el modal
$(document).on('show.bs.modal', '.modal', function () {
    $("#id_area").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 1.00});
    $("#id_ancho").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 1.00});
    $("#id_alto").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 1.00});
    $("#id_largo").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 1.00});
    $("#id_distancia_primera_fila").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 0.00});
    $("#id_area_por_alumno").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 0.00});
});