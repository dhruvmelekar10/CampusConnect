/**
 * CampusConnect - Client Script
 * VSIT (Vidyalankar School of Information Technology)
 */

document.addEventListener('DOMContentLoaded', function () {
  // Initialize Bootstrap tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Auto-dismiss alerts after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 6000);
  });

  // Image Preview handler for Item Reporting forms
  const imageInput = document.getElementById('imageUploadInput');
  const imagePreview = document.getElementById('imagePreview');
  const imagePreviewContainer = document.getElementById('imagePreviewContainer');

  if (imageInput && imagePreview && imagePreviewContainer) {
    imageInput.addEventListener('change', function (e) {
      const file = e.target.files[0];
      if (file) {
        // Validate file type
        const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
        if (!validTypes.includes(file.type)) {
          alert('Please select a valid image file (PNG, JPG, JPEG).');
          imageInput.value = '';
          imagePreviewContainer.classList.add('d-none');
          return;
        }

        // Validate max 5MB
        if (file.size > 5 * 1024 * 1024) {
          alert('Image size exceeds 5MB limit. Please choose a smaller file.');
          imageInput.value = '';
          imagePreviewContainer.classList.add('d-none');
          return;
        }

        const reader = new FileReader();
        reader.onload = function (event) {
          imagePreview.src = event.target.result;
          imagePreviewContainer.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
      } else {
        imagePreviewContainer.classList.add('d-none');
      }
    });
  }

  // Deletion confirmation helper
  const deleteForms = document.querySelectorAll('.confirm-delete-form');
  deleteForms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const itemName = form.getAttribute('data-item-name') || 'this record';
      const confirmed = confirm(`Are you sure you want to permanently delete ${itemName}? This action cannot be undone.`);
      if (!confirmed) {
        e.preventDefault();
      }
    });
  });

  // Setup Admin Charts if Chart.js is present and canvas elements exist
  if (typeof Chart !== 'undefined') {
    setupAdminCharts();
  }
});

function setupAdminCharts() {
  // 1. Lost vs Found Chart
  const lostVsFoundCanvas = document.getElementById('chartLostVsFound');
  if (lostVsFoundCanvas && window.adminChartData && window.adminChartData.lost_vs_found) {
    new Chart(lostVsFoundCanvas, {
      type: 'doughnut',
      data: {
        labels: window.adminChartData.lost_vs_found.labels,
        datasets: [{
          data: window.adminChartData.lost_vs_found.data,
          backgroundColor: ['#ef4444', '#10b981'],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });
  }

  // 2. Items by Category Chart
  const categoryCanvas = document.getElementById('chartCategories');
  if (categoryCanvas && window.adminChartData && window.adminChartData.categories) {
    new Chart(categoryCanvas, {
      type: 'bar',
      data: {
        labels: window.adminChartData.categories.labels,
        datasets: [{
          label: 'Total Items',
          data: window.adminChartData.categories.data,
          backgroundColor: '#0a2540',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0 } },
          x: { ticks: { autoSkip: false, maxRotation: 45, minRotation: 30 } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  // 3. Reports by Status Chart
  const statusCanvas = document.getElementById('chartStatuses');
  if (statusCanvas && window.adminChartData && window.adminChartData.statuses) {
    new Chart(statusCanvas, {
      type: 'pie',
      data: {
        labels: window.adminChartData.statuses.labels,
        datasets: [{
          data: window.adminChartData.statuses.data,
          backgroundColor: [
            '#38bdf8', // Open
            '#fbbf24', // Possible Match
            '#fb923c', // Claim Pending
            '#4ade80', // Claim Approved
            '#818cf8', // Returned
            '#94a3b8'  // Closed
          ],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });
  }
}
