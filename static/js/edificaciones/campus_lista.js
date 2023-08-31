$(function () {
    initDataTable();
});

function initDataTable() {
    table = $('#tabla-campus').DataTable({
        "processing": true,
        "serverSide": true,
        "stateSave": true,
        "order": [[0, "asc"]],
        "ajax": {
            "url": url_campus_lista,
            "type": "GET",
            "data": function (d) {
                d.sede_id = $('#filtro_sede').val();
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
            {"data": "sede"},
            {"data": "nombre"},
            {"data": "direccion"},
            {"data": "numero_bloques"},
        ],
        "columnDefs": [
            {
                orderable: false,
                targets: [3],
                className: 'text-center'
            },
            {targets: [1], render: function (data, type, row) {
                return '<a href="'+ url_campus_detalle + row.id +'">'+ row.nombre + ' (' + row.codigo +')</a>';
            }},
            {targets: [2], render: function (data, type, row) {
                var html = row.canton;
                if(row.direccion){
                    html += ': ' + row.direccion;
                }
                if(row.descripcion){
                    html += '<br><i class="fa fa-info-circle"></i> ' + row.descripcion;
                }
                return html;
            }},
            {targets: [3], render: function (data, type, row) {
                return '<span class="label label-default">'+ data + '</span>';
            }},
        ],
        "language": {"url": "/static/plugins/datatables/es.js"}
    });

    $('#filtro_sede').change(function (e) {
        table.draw();
    });
}