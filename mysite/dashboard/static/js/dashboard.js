/**
 * 대시보드의 모든 동적 기능을 관리하는 스크립트입니다.
 * - 사이드바 토글
 * - 페이지 전환 (SPA처럼 동작)
 * - 다크 모드 테마 전환 및 저장
 * - Chart.js를 이용한 차트 렌더링 및 테마 업데이트
 * - 사용자 상태 변경 및 검색
 */
document.addEventListener('DOMContentLoaded', () => {
    // 전역에서 사용할 차트 인스턴스 변수
    let dauChartInstance = null;
    let contentPieChartInstance = null;

    // --- DOM 요소 선택 ---
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const themeToggle = document.getElementById('theme-toggle');
    const sidebarLinks = document.querySelectorAll('.sidebar ul a');
    const quickLinks = document.querySelectorAll('.quick-link-card');
    const pageContents = document.querySelectorAll('.page-content');
    const celebrateBtn = document.getElementById('celebrate-btn');
    const userSearchInput = document.getElementById('user-search-input');
    const userTableRows = document.querySelectorAll('#user-central-content .data-table tbody tr');
    const statusToggleButtons = document.querySelectorAll('.btn-toggle-status');

    // --- 사이드바 기능 ---
    sidebarToggle.addEventListener('click', () => {
        document.body.classList.toggle('sidebar-open');
    });

    // --- 페이지 전환 기능 ---
    const setActivePage = (targetId) => {
        // 모든 링크에서 'active' 클래스 제거
        sidebarLinks.forEach(link => link.classList.remove('active'));
        // 모든 페이지 콘텐츠 숨기기
        pageContents.forEach(content => content.classList.remove('active'));

        // 대상 ID에 해당하는 링크와 콘텐츠에 'active' 클래스 추가
        const activeLink = document.querySelector(`.sidebar a[data-target="${targetId}"]`);
        const activeContent = document.getElementById(targetId);

        if (activeLink) {
            activeLink.classList.add('active');
        }
        if (activeContent) {
            activeContent.classList.add('active');
        }
    };

    const handleLinkClick = (event) => {
        const link = event.currentTarget;
        const targetId = link.dataset.target;

        // data-target 속성이 있는 링크만 처리
        if (targetId) {
            event.preventDefault();
            setActivePage(targetId);
        } else if (link.textContent === 'Support') {
            event.preventDefault();
            alert('지원 기능은 현재 준비 중입니다. 조금만 기다려주세요!');
        }
        // 'Quit' 링크는 기본 동작(href)을 따르도록 둡니다.
    };

    sidebarLinks.forEach(link => link.addEventListener('click', handleLinkClick));
    quickLinks.forEach(link => link.addEventListener('click', handleLinkClick));


    // --- 테마 전환 기능 ---
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        // 테마 변경 시 차트도 업데이트
        if (dauChartInstance) updateChartTheme(dauChartInstance, theme);
        if (contentPieChartInstance) updateChartTheme(contentPieChartInstance, theme);
    };

    const toggleTheme = () => {
        const newTheme = themeToggle.checked ? 'dark' : 'light';
        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);
    };

    // 페이지 로드 시 저장된 테마 적용
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        themeToggle.checked = savedTheme === 'dark';
        applyTheme(savedTheme);
    } else {
        // 시스템 기본 설정 확인
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        themeToggle.checked = prefersDark;
        applyTheme(prefersDark ? 'dark' : 'light');
    }

    themeToggle.addEventListener('change', toggleTheme);

    // --- 차트 렌더링 및 테마 업데이트 ---
    const getChartColors = (theme) => {
        const isDark = theme === 'dark';
        // CSS 변수에서 색상 값을 가져옵니다.
        const style = getComputedStyle(document.documentElement);
        return {
            gridColor: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)',
            ticksColor: style.getPropertyValue('--card-header-color').trim(),
            labelColor: style.getPropertyValue('--heading-color').trim(),
            pieBorderColor: style.getPropertyValue('--bg-color').trim(),
        };
    };

    const updateChartTheme = (chartInstance, theme) => {
        const colors = getChartColors(theme);
        const chartType = chartInstance.config.type;

        if (chartType === 'bar' || chartType === 'line') {
            chartInstance.options.scales.x.grid.color = colors.gridColor;
            chartInstance.options.scales.y.grid.color = colors.gridColor;
            chartInstance.options.scales.x.ticks.color = colors.ticksColor;
            chartInstance.options.scales.y.ticks.color = colors.ticksColor;
        }
        chartInstance.options.plugins.legend.labels.color = colors.labelColor;
        if (chartType === 'doughnut' || chartType === 'pie') {
            chartInstance.data.datasets[0].borderColor = colors.pieBorderColor;
        }

        chartInstance.update();
    };

    const createDauChart = () => {
        const canvas = document.getElementById('dauChart');
        if (!canvas || !window.Chart || !canvas.dataset.labels || !canvas.dataset.values) return null;

        try {
            const labels = JSON.parse(canvas.dataset.labels);
            const data = JSON.parse(canvas.dataset.values);
            const theme = document.documentElement.getAttribute('data-theme') || 'light';
            const colors = getChartColors(theme);

            const ctx = canvas.getContext('2d');
            return new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '일간 활성 사용자 수',
                        data: data,
                        backgroundColor: 'rgba(63, 167, 106, 0.5)',
                        borderColor: 'rgba(63, 167, 106, 1)',
                        borderWidth: 1,
                        borderRadius: 4,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { color: colors.gridColor, borderColor: colors.gridColor },
                            ticks: { color: colors.ticksColor }
                        },
                        y: {
                            beginAtZero: true,
                            grid: { color: colors.gridColor, borderColor: colors.gridColor },
                            ticks: {
                                color: colors.ticksColor,
                                stepSize: 1,
                                precision: 0
                            }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(0,0,0,0.7)',
                            titleFont: { size: 14 },
                            bodyFont: { size: 12 },
                            padding: 10,
                        }
                    }
                }
            });
        } catch (e) {
            console.error('DAU 차트 데이터 파싱 또는 생성 중 오류 발생:', e);
            return null;
        }
    };

    const createContentPieChart = () => {
        const canvas = document.getElementById('contentPieChart');
        if (!canvas || !window.Chart || !canvas.dataset.labels || !canvas.dataset.values) return null;

        try {
            const labels = JSON.parse(canvas.dataset.labels);
            const data = JSON.parse(canvas.dataset.values);
            const theme = document.documentElement.getAttribute('data-theme') || 'light';
            const colors = getChartColors(theme);

            const ctx = canvas.getContext('2d');
            return new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '콘텐츠 수',
                        data: data,
                        backgroundColor: ['#3fa76a', '#6c8bc7', '#f0c987', '#b05c90', '#5c4fa3'],
                        borderColor: colors.pieBorderColor,
                        borderWidth: 3,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '65%',
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                color: colors.labelColor,
                                boxWidth: 12,
                                padding: 15
                            }
                        }
                    }
                }
            });
        } catch (e) {
            console.error('콘텐츠 분포 차트 데이터 파싱 또는 생성 중 오류 발생:', e);
            return null;
        }
    };

    // --- 사용자 관리 기능 ---
    const getCookie = (name) => {
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
    };
    const csrftoken = getCookie('csrftoken');

    // 사용자 검색
    if (userSearchInput) {
        const userTableBody = document.querySelector('#user-central-content .data-table tbody');

        userSearchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            let visibleRows = 0;

            userTableRows.forEach(row => {
                if (row.cells.length <= 1) return; // '사용자 없음' 행은 무시

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

    // 사용자 상태 토글
    statusToggleButtons.forEach(button => {
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

    // --- 기타 기능 ---
    celebrateBtn.addEventListener('click', () => {
        if (window.confetti) {
            confetti({
                particleCount: 150,
                spread: 90,
                origin: { y: 0.6 }
            });
        }
    });

    // --- 초기화 ---
    const initializeDashboard = () => {
        // 페이지 로드 시 URL 해시(#) 값에 상관없이 항상 'home-content'를 기본으로 표시합니다.
        // 이렇게 하면 사용자가 어떤 링크로 들어오든 초기 화면은 동일하게 유지됩니다.
        const defaultPageId = 'home-content';
        setActivePage(defaultPageId);

        // 차트 생성
        dauChartInstance = createDauChart();
        contentPieChartInstance = createContentPieChart();
    };

    initializeDashboard();

}); // End of DOMContentLoaded
