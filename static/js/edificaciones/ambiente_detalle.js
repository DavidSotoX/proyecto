$(document).on('show.bs.modal', '.modal', function () {
    if ($("#id_area").length > 0) {
        $("#id_area").autoNumeric('init', { aSep: '', aDec: '.', mDec: 2, vMin: 1.00 });
        $("#id_ancho").autoNumeric('init', { aSep: '', aDec: '.', mDec: 2, vMin: 1.00 });
        $("#id_alto").autoNumeric('init', { aSep: '', aDec: '.', mDec: 2, vMin: 1.00 });
        $("#id_largo").autoNumeric('init', { aSep: '', aDec: '.', mDec: 2, vMin: 1.00 });
        $("#id_distancia_primera_fila").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 0.00});
        $("#id_area_por_alumno").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 0.00});

        $("#div_id_codigo_puerta").css("margin-top", "35px");
    }
});

$(function () {
    initDataTable();
});

function initDataTable() {
    table = $('#tabla-ambiente-usos').DataTable({
        "processing": true,
        "serverSide": true,
        "stateSave": true,
        "order": [[0, "asc"]],
        "ajax": {
            "url": url_ambiente_uso_lista,
            "type": "GET",
            "data": function (d) {
            },
            "error": function (err) {
                // sesión caducada
                if (err.status == 401) {
                    alert_notificacion('Error', err.responseJSON.detail, 'error').then((result) => {
                        window.location = window.location;
                    });
                } else {
                    mensaje_error(err.responseJSON.detail);
                }
            }
        },
        "columns": [
            { "data": "revision_fecha" },
            { "data": "usuario" },
            { "data": "uso_tipo" },
            { "data": "codigo" },
            { "data": "dependencia" },
            { "data": "aula" },
            { "data": "subambientes" },
        ],
        "columnDefs": [
            {
                orderable: false,
                targets: [5, 6],
            },
            {
                targets: [0], render: function (data, type, row) {
                    return '<a href="' + url_ambiente_uso_detalle + row.id + '">' + data + '</a>';
                }
            },
            {
                targets: [6], render: function (data, type, row) {
                    var html = '';
                    for (var i = 0; i < data.length; i++) {
                        html += '<i class="fa fa-home"></i> ' + data[i].codigo + '-' + data[i].nombre + '<br>'
                    }
                    return html;
                }
            },
        ],
        "language": { "url": "/static/plugins/datatables/es.js" }
    });
}
