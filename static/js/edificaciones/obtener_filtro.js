function obtenerValoresFiltros() {
    var valor_campus_id = $('#filtro_campus').val();
    var valor_bloque_id = $('#filtro_bloque').val();
    var valor_numero_piso = $('#filtro_numero_piso').val();
    var valor_dependencia_id = $('#filtro_dependencia').val();
    var valor_año_id = $('#filtro_año').val();

    return {
        campus_id: valor_campus_id,
        bloque_id: valor_bloque_id,
        numero_piso: valor_numero_piso,
        dependencia_id: valor_dependencia_id,
        año_id: valor_año_id
    };
}
