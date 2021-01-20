var dnIncome = document.getElementById('pieRevenue').getContext('2d');
var dnSold = document.getElementById('pieSellers').getContext('2d');

var sold = new Chart(dnSold, {
    type: 'pie',
    data: {
        datasets: [{
            data: [10, 20, 30],
            backgroundColor: ['#f3545d','#fdaf4b','#1d7af3']
        }],

        labels: [
        'Ноутбуки',
        'ТВ',
        'Смартфоны'
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        legend : {
            position: 'left'
        },
        layout: {
            padding: {
                left: 20,
                right: 20,
                top: 20,
                bottom: 20
            }
        }
    }
});

var income = new Chart(dnIncome, {
    type: 'pie',
    data: {
        datasets: [{
            data: [10, 20, 30],
            backgroundColor: ['#f3545d','#fdaf4b','#1d7af3']
        }],

        labels: [
        'Ноутбуки',
        'ТВ',
        'Смартфоны'
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        legend : {
            position: 'left'
        },
        layout: {
            padding: {
                left: 20,
                right: 20,
                top: 20,
                bottom: 20
            }
        }
    }
});