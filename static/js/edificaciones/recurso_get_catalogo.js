$(document).ready(function () {
    var catalogoCol = $('#div_id_catalogo');
    var initialCatalogo = ""; // almacenar valor inicial de catalogo
    console.log(initialCatalogo)

    function mostrarOcultarCatalogoCol() {
        if ($('#id_tipo').val() === 'CATALOGO') {
            catalogoCol.show();
            $('#id_catalogo').prop('required', true);
        } else {
            $('#id_catalogo').val(initialCatalogo); // asignar valor inicial a catalogo
            catalogoCol.hide();
        }
    }

    mostrarOcultarCatalogoCol();

    $('#id_tipo').change(function () {
        mostrarOcultarCatalogoCol();
    });
});