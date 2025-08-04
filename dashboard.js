// 사이드바 토글 기능
document.getElementById('sidebar-toggle').addEventListener('click', function() {
    document.body.classList.toggle('sidebar-open');
});

// 사이드바 메뉴 및 페이지 전환 처리
const sidebarLinks = document.querySelectorAll('.sidebar ul a');
const supportButton = document.querySelector('.sidebar .support button');
const pageContents = document.querySelectorAll('.page-content');

// 사이드바 클릭 이벤트
sidebarLinks.forEach(link => {
    link.addEventListener('click', function(event) {
        const targetId = this.dataset.target;

        // 'Quit' 처리
        if (this.textContent === 'Quit') {
            event.preventDefault();
            if (confirm('정말로 로그아웃 하시겠습니까?')) {
                window.location.href = this.href;
            }
            return;
        }

        // 'Support' 처리
        if (this.textContent === 'Support') {
            event.preventDefault();
            alert('도움이 필요하시면 하단의 "Start" 버튼을 눌러주세요.');
            return;
        }

        // 일반 메뉴 처리
        if (targetId) {
            event.preventDefault();

            // active 초기화
            sidebarLinks.forEach(l => l.classList.remove('active'));
            pageContents.forEach(p => p.classList.remove('active'));

            // active 적용
            this.classList.add('active');
            const targetPage = document.getElementById(targetId);
            if (targetPage) targetPage.classList.add('active');
        }
    });
});

// 기본 페이지 활성화 (초기 진입 시)
window.addEventListener('DOMContentLoaded', () => {
    const defaultActiveLink = document.querySelector('.sidebar a[data-target="access-requests-content"]');
    const defaultPage = document.getElementById('access-requests-content');
    if (defaultActiveLink) defaultActiveLink.classList.add('active');
    if (defaultPage) defaultPage.classList.add('active');

    // --- 다크/라이트 모드 토글 기능 ---
    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') themeToggle.checked = true;
    }

    themeToggle.addEventListener('change', function() {
        const theme = this.checked ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    });

    // --- 사용자 검색 ---
    const searchInput = document.getElementById('user-search-input');
    if (searchInput) {
        const userTableBody = document.querySelector('#user-central-content .data-table tbody');
        const userTableRows = userTableBody.querySelectorAll('tr');

        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            let visibleRows = 0;

            userTableRows.forEach(row => {
                if (row.cells.length <= 1) return;

                const username = row.cells[0].textContent.toLowerCase();
                const email = row.cells[1].textContent.toLowerCase();
                const name = row.cells[2].textContent.toLowerCase();

                if (username.includes(searchTerm) || email.includes(searchTerm) || name.includes(searchTerm)) {
                    row.style.display = '';
                    visibleRows++;
                } else {
                    row.style.display = 'none';
                }
            });

            let noResultsRow = userTableBody.querySelector('.no-search-results');
            if (visibleRows === 0 && searchTerm !== '' && !noResultsRow) {
                noResultsRow = userTableBody.insertRow();
                noResultsRow.className = 'no-search-results';
                noResultsRow.innerHTML = `<td colspan="6" style="text-align: center; padding: 40px;">'${this.value}'에 대한 검색 결과가 없습니다.</td>`;
            } else if ((visibleRows > 0 || searchTerm === '') && noResultsRow) {
                noResultsRow.remove();
            }
        });
    }

    // --- 사용자 상태 토글 기능 ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    document.querySelectorAll('.btn-toggle-status').forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.url;
            const button = this;

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.message || '서버 오류가 발생했습니다.') });
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    const row = button.closest('tr');
                    const statusSpan = row.querySelector('.status-span');

                    if (data.is_active) {
                        statusSpan.className = 'status-span status-active';
                        statusSpan.textContent = '활성';
                        button.className = 'btn-toggle-status btn-deactivate';
                        button.textContent = '비활성화';
                    } else {
                        statusSpan.className = 'status-span status-inactive';
                        statusSpan.textContent = '비활성';
                        button.className = 'btn-toggle-status btn-activate';
                        button.textContent = '활성화';
                    }
                } else {
                    alert('오류: ' + data.message);
                }
            })
            .catch(error => {
                alert('요청 처리 중 오류가 발생했습니다: ' + error.message);
            });
        });
    });

    // 지원 버튼 처리
    supportButton.addEventListener('click', () => {
        alert('지원 채널은 현재 준비 중입니다. 곧 찾아뵙겠습니다!');
    });
});

// --- 일간 활성 사용자 바 차트 ---
const dauChartCanvas = document.getElementById('dauChart');
if (typeof Chart !== 'undefined' && dauChartCanvas && dauChartCanvas.dataset.labels && dauChartCanvas.dataset.values) {
    let labels, data;
    try {
        labels = JSON.parse(dauChartCanvas.dataset.labels);
        data = JSON.parse(dauChartCanvas.dataset.values);
    } catch (e) {
        // 이 부분의 경고는 1단계에서 해결되었습니다.
        console.error('일간 활성 사용자 데이터를 파싱하는 데 실패했습니다:', e);
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
                        ticks: {
                            stepSize: 1,
                            precision: 0
                        }
                    }
                },
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}

// --- 전체 콘텐츠 분포 도넛 그래프 ---
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