function campus_get_bloques(campus_id, elemento){
    $(elemento).empty();
    $(elemento).append('<option value="">-- Seleccione --</option>');

    if (campus_id != '') {

        $.ajax({
            type: 'GET',
            url: url_campus_bloques + campus_id,
            processData: false,
            contentType: false,
            success: function (data, ajaxOptions, thrownError) {
                for (var i = 0; i < data.data.length; i++) {
                    $(elemento).append('<option value="' + data.data[i]['id'] + '">' + data.data[i]['numero'] + '</option>');
                }
            },
            error: function (error) {
                // sesión caducada
                if (error.status == 401){
                    alert_notificacion('Error', error.responseJSON.detail, 'error').then((result) => {
                        window.location = window.location;
                    });
                }else{
                    if (error.responseJSON && error.responseJSON.detail){
                        mensaje_error(error.responseJSON.detail);
                    } else{
                        mensaje_error("Error en la petición (" + error.statusText + ').');
                    }
                }
            }
        });
    }
}