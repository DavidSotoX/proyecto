// exportar.js
document.getElementById("exportarBtn").addEventListener("click", function () {
    var valoresFiltros = obtenerValoresFiltros();

    // Verificar si se han aplicado filtros
    var filtrosAplicados = (valoresFiltros.campus_id !== '' || valoresFiltros.bloque_id !== '' || valoresFiltros.numero_piso !== '' || valoresFiltros.dependencia_id !== '' || valoresFiltros.año_id !== '');

    var jsonData = {};
    if (filtrosAplicados) {
        jsonData.selectores = valoresFiltros;
    }

    window.location.href = ambienteXlsDetalladoUrl + "?data=" + encodeURIComponent(JSON.stringify(jsonData));
});
