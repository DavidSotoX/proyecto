$(function () {
    initDataTable();
});

function initDataTable() {
    table = $('#tabla-bloques').DataTable({
        "processing": true,
        "serverSide": true,
        "stateSave": true,
        "order": [[0, "asc"]],
        "ajax": {
            "url": url_bloque_lista,
            "type": "GET",
            "data": function (d) {
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
            {"data": "numero"},
            {"data": "numero_pisos"},
            {"data": "numero_ambientes"},
            {'data': "id"}
        ],
        "columnDefs": [
            {
                orderable: false,
                targets: [2],
            },
            {
                orderable: false,
                targets: [3],
                className: 'tabla-accion'
            },
            {targets: [2], render: function (data, type, row) {
                var html = '<span class="label label-default">'+ data +'</span>';
                return html;
            }},
            {targets: [3], render: function (data, type, row) {
                var html = '<div class="btn-group">';

                if (row.puede_editar == true){
                    html += '<button data-url="'+ url_bloque_editar + row.id +'" ' +
                            'class="btn btn-success btn-xs abrir-modal-editar" ' +
                            'data-modal-titulo="Editar bloque" ' +
                            'data-size="modal-lg" ' +
                            'title="Editar registro">' +
                            '<i class="fa fa-edit"></i>' +
                            '</button>';
                }

                if (row.puede_eliminar == true){
                    html += '<a href="'+ url_bloque_eliminar + row.id +'" ' +
                            'class="btn btn-danger btn-xs" ' +
                            'title="Eliminar bloque">' +
                            '<i class="fa fa-trash"></i>' +
                            '</a>';
                }

                html += '</div>';

                return html;
            }},
        ],
        "language": {"url": "/static/plugins/datatables/es.js"}
    });

    $('#filtro_sede').change(function (e) {
        table.draw();
    });
}