// charts.js

// DAU 차트
const dauChartCanvas = document.getElementById('dauChart');
if (typeof Chart !== 'undefined' && dauChartCanvas && dauChartCanvas.dataset.labels && dauChartCanvas.dataset.values) {
    let labels, data;
    try {
        labels = JSON.parse(dauChartCanvas.dataset.labels);
        data = JSON.parse(dauChartCanvas.dataset.values);
    } catch (e) {
        console.warn('일간 활성 사용자 데이터를 파싱할 수 없습니다.', e);
    }

    if (Array.isArray(labels) && Array.isArray(data)) {
        const ctx = dauChartCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '일간 활성 사용자 수',
                    data: data,
                    backgroundColor: 'rgba(63, 167, 106, 0.2)',
                    borderColor: 'rgba(63, 167, 106, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, precision: 0 }
                    }
                },
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    }
}

// 콘텐츠 분포 도넛 차트
const contentPieChartCanvas = document.getElementById('contentPieChart');
if (typeof Chart !== 'undefined' && contentPieChartCanvas && contentPieChartCanvas.dataset.labels && contentPieChartCanvas.dataset.values) {
    const contentLabels = JSON.parse(contentPieChartCanvas.dataset.labels);
    const contentData = JSON.parse(contentPieChartCanvas.dataset.values);
    const ctx = contentPieChartCanvas.getContext('2d');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: contentLabels,
            datasets: [{
                label: '콘텐츠 수',
                data: contentData,
                backgroundColor: ['#3fa76a', '#6c8bc7', '#f0c987', '#b05c90', '#5c4fa3'],
                borderColor: 'rgba(255, 255, 255, 0.9)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: { boxWidth: 12, padding: 15 }
                }
            }
        }
    });
}
