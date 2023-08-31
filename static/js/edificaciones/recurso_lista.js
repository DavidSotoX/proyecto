$(function () {
    initDataTable();
});

function initDataTable() {
    table = $('#tabla-recurso').DataTable({
        "processing": true,
        "serverSide": true,
        "stateSave": true,
        "order": [[0, "asc"]],
        "ajax": {
            "url": url_recurso_lista,
            "type": "GET",
            "data": function (d) {
                d.activo = $('#filtro_activo').val();
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
            { "data": "orden" },
            { "data": "nombre" },
            { "data": "activo" },
            { "data": "numero_items" },
        ], 
        "columnDefs": [
            {
                orderable: false,
                targets: [2],
                className: 'text-center'
            },
            {
                targets: [1], render: function (data, type, row) {
                    return '<a href="' + url_recurso_detalle + row.id + '">' + row.nombre;
                }
            },
            {
                targets: [2], render: function (data, type, row) {
                    if (row.activo == true) {
                        return '<span class="badge badge-pill badge-success">Sí</span>'
                    } else {
                        return '<span class="badge badge-pill badge-danger">No</span>'

                    }
                }
            },
            {
                targets: [3], render: function (data, type, row) {
                    return '<span class="label label-default">' + data + '</span>';
                }
            },
        ],
        "language": { "url": "/static/plugins/datatables/es.js" }
    });

    $('#filtro_activo').change(function (e) {
        table.draw();
    });
}