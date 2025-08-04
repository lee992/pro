// sidebar.js

// 사이드바 열기/닫기
document.getElementById('sidebar-toggle').addEventListener('click', function () {
    document.body.classList.toggle('sidebar-open');
});

// 사이드바 페이지 전환
const sidebarLinks = document.querySelectorAll('.sidebar ul a');
const pageContents = document.querySelectorAll('.page-content');

sidebarLinks.forEach(link => {
    link.addEventListener('click', function (event) {
        const targetId = this.dataset.target;

        if (this.textContent === 'Quit') {
            event.preventDefault();
            if (confirm('정말로 로그아웃 하시겠습니까?')) {
                window.location.href = this.href;
            }
            return;
        }

        if (this.textContent === 'Support') {
            event.preventDefault();
            alert('도움이 필요하시면 하단의 "Start" 버튼을 눌러주세요.');
            return;
        }

        if (targetId) {
            event.preventDefault();
            sidebarLinks.forEach(l => l.classList.remove('active'));
            pageContents.forEach(p => p.classList.remove('active'));

            this.classList.add('active');
            const targetPage = document.getElementById(targetId);
            if (targetPage) targetPage.classList.add('active');
        }
    });
});

// 초기 페이지 활성화 및 테마 설정
window.addEventListener('DOMContentLoaded', () => {
    const defaultActiveLink = document.querySelector('.sidebar a[data-target="access-requests-content"]');
    const defaultPage = document.getElementById('access-requests-content');
    if (defaultActiveLink) defaultActiveLink.classList.add('active');
    if (defaultPage) defaultPage.classList.add('active');

    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') themeToggle.checked = true;
    }

    themeToggle.addEventListener('change', function () {
        const theme = this.checked ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    });
});
