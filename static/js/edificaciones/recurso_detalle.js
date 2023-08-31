$(function () {
    initDataTable();
});

function initDataTable() {
    table = $('#tabla-recursoitem').DataTable({
        "processing": true,
        "serverSide": true,
        "stateSave": true,
        "order": [[0, "asc"]],
        "ajax": {
            "url": url_recursoitem_lista,
            "type": "GET",
            "data": function (d) {
                d.tipo = $('#filtro_tipo').val();
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
            { "data": "tipo" },
            { "data": "catalogo" },
            { "data": "activo" },
        ],
        "columnDefs": [
            {
                orderable: false,
                targets: [5],
                className: 'tabla-accion'
            },
            {
                targets: [3], render: function (data, type, row) {
                    if (row.items && row.catalogo) {
                        // items
                        var itemsHtml = '<ul>';
                        row.items.forEach(function (item) {
                            var activo = (row.catalogo.activo && item.activo == false) ? '<span class="label label-danger">INACTIVO</span>' : '';
                            itemsHtml += '<li>' + item.nombre + ' ' + activo + '</li>';
                        });
                        itemsHtml += '</ul>';
                        // catalogo
                        activo = row.catalogo.activo ? '' : '<span class="label label-danger">INACTIVO</span>';
                        var html = '<strong class="text-uppercase font-weight-bold">' + row.catalogo.nombre + ' ' + activo + '</strong>' + itemsHtml;
                        return html;
                    } else {
                        return "";
                    }
                }
            },
            {
                targets: [4], render: function (data, type, row) {
                    if (row.activo == true) {
                        return '<span class="badge badge-pill badge-success">Sí</span>'
                    } else {
                        return '<span class="badge badge-pill badge-danger">No</span>'

                    }
                }
            },
            {
                targets: [5], render: function (data, type, row) {
                    var html = '<div class="btn-group">';

                    if (row.puede_editar == true) {
                        html += '<button data-url="' + url_recursoitem_editar + row.id + '" ' +
                            'class="btn btn-success btn-xs abrir-modal-editar" ' +
                            'data-modal-titulo="Editar Item" ' +
                            'data-size="modal-lg" ' +
                            'title="Editar registro">' +
                            '<i class="fa fa-edit"></i>' +
                            '</button>';
                    }

                    if (row.puede_eliminar == true) {
                        html += '<a href="' + url_recursoitem_eliminar + row.id + '" ' +
                            'class="btn btn-danger btn-xs" ' +
                            'title="Eliminar Item">' +
                            '<i class="fa fa-trash"></i>' +
                            '</a>';
                    }

                    html += '</div>';

                    return html;
                }
            },
        ],
        "language": { "url": "/static/plugins/datatables/es.js" }
    });
    $('#filtro_tipo').change(function (e) {
        table.draw();
    });
}