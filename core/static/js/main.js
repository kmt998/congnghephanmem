// core/static/js/main.js — JavaScript dùng chung cho toàn hệ thống

// Tự động đóng thông báo flash sau 4 giây
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 300);
    }, 4000);
  });
});

// Chuyển tab giao diện
function showTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));

  const activeBtn = document.getElementById('tab-' + tabName);
  const activePanel = document.getElementById('panel-' + tabName);

  if (activeBtn) activeBtn.classList.add('active');
  if (activePanel) activePanel.classList.add('active');
}
