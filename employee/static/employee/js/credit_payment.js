document.addEventListener("DOMContentLoaded", () => {
    const calc_button = document.getElementById('calc_button');

    if (calc_button) {
        calc_button.addEventListener('click', function () {
            const credit_date_el = document.getElementById('id_credit_date');
            const date_first_payment_el = document.getElementById('id_date_first_payment');
            const credit_amount_el = document.getElementById('id_credit_amount');
            const payments_count_el = document.getElementById('id_payments_count');
            const tbody = document.querySelector('.tabular.inline-related tbody');

            let payments_count = payments_count_el.value ?? 0;

            const payment_amount_el = document.getElementById('id_payment_amount')
            if (payment_amount_el.value) {
                payments_count = payment_amount_el.value ? Math.ceil(credit_amount_el.value / payment_amount_el.value) : 0;
                payments_count_el.value = payments_count;
            }

            if (!payments_count) {
                alert('Введите период')
            } else {
                let credit_amount = credit_amount_el.value;
                let payment_amount = payment_amount_el.value ? payment_amount_el.value : Math.ceil(credit_amount / payments_count)
                const payments= [];
                let date = credit_date_el.value;
                const pattern = /(\d{2})\.(\d{2})\.(\d{4})/;
                date = new Date(date.replace(pattern, '$3-$2-$1'));
                tbody.innerHTML += `<tr><td></td><td>${date.toLocaleDateString()}</td><td>${-credit_amount}</td><td></td><td></td><td></td></tr>`;
                payments.push({'date': date, 'payment_amount': -credit_amount });
                date = date_first_payment_el.value;
                date = new Date(date.replace(pattern, '$3-$2-$1'));

                for (let i = 0; i < payments_count; i++) {
                    if (credit_amount <= payment_amount) {
                        payment_amount = credit_amount
                    } else {
                        credit_amount -= payment_amount;
                    }
                    let newDate = new Date(date);
                    tbody.innerHTML += `<tr><td></td><td>${newDate.toLocaleDateString()}</td><td>${payment_amount}</td><td></td><td></td><td></td></tr>`;
                    payments.push({'date': newDate, 'payment_amount':payment_amount});
                    date.setMonth(date.getMonth() + 1)

                }

            }

        })
    }
});