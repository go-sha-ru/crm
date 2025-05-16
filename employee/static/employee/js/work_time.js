document.addEventListener("DOMContentLoaded", () => {
    const employee_group = document.getElementById('id_employee_group');
    const month = document.getElementById('id_date');
    const rows_total = document.querySelectorAll('.row_total');
    const columns_total = document.querySelectorAll('.column_total');
    let report_title = document.getElementById('report_title');
    const report_table = document.getElementById('report_table');
    const save_csv = document.getElementById('save_csv')

    if (report_title) {
        report_title = report_title.innerText;
    }

    if (employee_group) {
        employee_group.addEventListener('change', (e) => {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('employee_group', e.target.value);
            window.location.search = urlParams;
        });
    }
    if (month) {
        month.addEventListener('change', (e) => {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('date', e.target.value);
            window.location.search = urlParams;
        });
    }
    if (rows_total) {
        rows_total.forEach(e => {
            let sum = 0;
            e.parentNode.querySelectorAll('.hours').forEach(el => {
                sum += Number(el.innerHTML);
            })
            e.innerHTML = sum;
        })
    }

    if (columns_total) {
        columns_total.forEach(e => {
            let col = e.getAttribute('data-col');
            let sum = 0;
            document.querySelectorAll('.col_'+col).forEach(el => {
                sum += Number(el.innerHTML);
            })
            if (sum !== 0)e.innerHTML = sum;
        })
    }

    if (save_csv) {
        save_csv.addEventListener('click', function (e) {
            e.stopPropagation();
            const data = exportCSV();
            this.setAttribute('href', data);
            this.setAttribute('download', 'data.csv');
        })
    }

    if (report_table) {
        function exportCSV() {
            let rows = [];
            let row = [];
            row.push(report_title);
            rows.push(row);
            row = [''];
            rows.push(row);
            row = [];
            const thead = report_table.getElementsByClassName('thead');
            for (let el of thead) {
                row.push(el.innerHTML);
            }
            rows.push(row);

            const tdata = report_table.getElementsByClassName('tdata');
            for (let el of tdata) {
                row = [];
                let tds = el.querySelectorAll('td');
                tds.forEach(td => {
                    row.push(td.innerText);
                })
                rows.push(row);
            }
            row = [];
            const tfoot = report_table.getElementsByClassName('tfoot');
            for (let el of tfoot) {
                row.push(el.innerText);
            }
            rows.push(row);

            let csvContent = "data:text/csv;charset=utf-8,";

            rows.forEach(function(rowArray) {
                let r = rowArray.join(",");
                csvContent += r + "\r\n";
            });
            return csvContent;
        }
    }

    let hours = document.querySelectorAll('.hours');

    if (hours) {
        hours.forEach(el => {
            el.addEventListener('click', function (e) {
                // const oper = this.innerText ? '/change' : 'add';
                const oper = 'add';
                const obj_id = this.getAttribute('data-id');
                let url = '';
                if (document.getElementById('is_hours').getAttribute('data-is_hours') === 'True') {
                    url = '/admin/employee/employeetime/'
                } else {
                    url = '/admin/employee/employeeworkitem/'
                }

                if (obj_id) url += obj_id
                url += oper +'/?_to_field=id&_popup=1';
                url += '&employee=' + this.getAttribute('data-employee_id');
                url += '&date=' + this.getAttribute('data-day');
                const win = window.open(url, 'name', 'height=600,width=900,resizable=yes,scrollbars=yes');
                win.focus();
            })
        })
    }

})