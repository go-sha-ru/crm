document.addEventListener("DOMContentLoaded", () => {
    const salary_view = document.getElementById('id_salary_view');
    const employee_group = document.getElementById('id_employee_group');
    const id_file = document.getElementById('id_file');
    const upload = document.getElementById('id_upload');

    const items = document.querySelectorAll('.item-open');

    if (items) {
        items.forEach(function (el) {
            el.addEventListener('click', function () {
                const groupId = this.dataset.groupId;
                const salaryId = this.parentNode.dataset.salaryId;
                const employeeId = this.parentNode.dataset.employeeId;
                let addUrl = this.parentNode.dataset.addUrl;
                addUrl += '?_to_field=id&_popup=1&employee_id=' + employeeId + '&group_id=' + groupId + '&salary_id=' + salaryId;
                const a = document.createElement('a');
                a.classList.add('related-widget-wrapper-link', 'add-related');
                a.href = addUrl;
                a.setAttribute('data-popup', "yes");
                document.body.appendChild(a);
                a.click();
            })
        })
    }

    if (id_file) {
        id_file.addEventListener('change', e => {
            upload.disabled = false;
        })
    }

    if (salary_view) {
        salary_view.addEventListener('change', (e) => {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('salary_view', e.target.value);
            window.location.search = urlParams;
        });
    }
    
    if (employee_group) {
        employee_group.addEventListener('change', (e) => {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('employee_group', e.target.value);
            window.location.search = urlParams;
        });
    }    
        
    window.printLandscape = function () {
        const style = document.createElement('style');
        style.innerHTML = `@media print {@page {size:landscape;}}`;
        document.title = '';
        document.head.appendChild(style);
        window.print();
    };
    
    window.printPortrait = function () {
        const style = document.createElement('style');
        style.innerHTML = `@media print {@page {size:portrait;}}`;
        document.title = '';
        document.head.appendChild(style);
        window.print();
    };

});

