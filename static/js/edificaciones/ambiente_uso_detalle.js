$(document).on('show.bs.modal', '.modal', function () {
    if ($("#id_area").length>0){
        $("#id_area").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 1.00});
        $("#id_ancho").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 1.00});
        $("#id_alto").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 1.00});
        $("#id_largo").autoNumeric('init', {aSep: '', aDec: '.', mDec: 2, vMin: 1.00});

        $("#id_codigo_puerta").css("margin-top", "20px");
        $("#id_codigo_puerta").css("margin-left", "0");
    }
});