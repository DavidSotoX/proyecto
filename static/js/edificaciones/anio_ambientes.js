document.addEventListener('DOMContentLoaded', function() {
    const filtroAño = document.getElementById('filtro_año');
    
    filtroAño.addEventListener('change', function() {
        const selectedYear = filtroAño.value;
        
        // Realizar una solicitud AJAX
        const xhr = new XMLHttpRequest();
        xhr.open('GET', `/ambiente/años/?year=${selectedYear}`, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // Manejar la respuesta aquí (actualizar la página o elementos)
                const response = JSON.parse(xhr.responseText);
                const uniqueYears = response.unique_years;
                updateYearOptions(uniqueYears); // Llama a la función para actualizar opciones
            }
        };
        xhr.send();
    });
    
    function updateYearOptions(years) {
        const select = document.getElementById('filtro_año');
        select.innerHTML = '<option value="" selected>--Todos--</option>'; // Limpiar opciones
        years.forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            select.appendChild(option);
        });
    }
});
