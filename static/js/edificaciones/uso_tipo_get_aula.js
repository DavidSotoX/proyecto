$(document).ready(function () {

    function hideAulaForm() {
        $('#aula_form').hide();
        $("#id_distancia_primera_fila, #id_area_por_alumno").prop("required", false).val('');
        removeErrorAsterisk("id_distancia_primera_fila");
        removeErrorAsterisk("id_area_por_alumno");
    }

    function showAulaForm(aula) {
        $('#aula_form').show();
        $("#id_distancia_primera_fila, #id_area_por_alumno").prop("required", true);
        addErrorAsterisk("id_distancia_primera_fila");
        addErrorAsterisk("id_area_por_alumno");
    }

    function handleUsoTipoChange() {
        if ($("#id_uso_tipo option:selected").attr('data-es-aula') == null) {
            hideAulaForm();
        } else {
            showAulaForm();
        }
    }

    function addErrorAsterisk(elementId) {
        var label = $("label[for='" + elementId + "']");
        if ($("#" + elementId).prop("required") && !label.has(".error").length) {
            label.prepend("<span class='error'>(*) </span>");
        }
    }

    function removeErrorAsterisk(elementId) {
        var label = $("label[for='" + elementId + "']");
        label.find(".error").remove();
    }

    $('#id_uso_tipo').on('change', handleUsoTipoChange);
    handleUsoTipoChange();

});
