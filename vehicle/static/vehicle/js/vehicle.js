document.addEventListener("DOMContentLoaded", () => {
    const projects = document.getElementById('id_project');
    const work = document.getElementById('id_work');
    const special_vehicle_type = document.getElementById('id_special_vehicle_type');
    const special_vehicle = document.getElementById('id_special_vehicle');

    if (projects) {
        projects.addEventListener('change', function () {
            const project_id = this.value;
            fetch("//localhost:8080/api/project/works?project_id=" + project_id)
                .then(data => {
                    return data.json()
                })
                .then(data => {
                    work.innerHTML = '<option value="" selected="">---------</option>';
                    data.forEach(el => {
                        const option = document.createElement('option');
                        option.value = el.id
                        option.text = el.title
                        work.appendChild(option)
                    })
                })
        })
    }
    if (special_vehicle_type) {
        special_vehicle_type.addEventListener('change', function () {
            const type_id = this.value;
                        fetch("//localhost:8080/api/vehicle?type_id=" + type_id)
                .then(data => {
                    return data.json()
                })
                .then(data => {
                    special_vehicle.innerHTML = '<option value="" selected="">---------</option>';
                    data.forEach(el => {
                        const option = document.createElement('option');
                        option.value = el.id
                        option.text = el.model
                        special_vehicle.appendChild(option)
                    })
                })

        })
    }

})