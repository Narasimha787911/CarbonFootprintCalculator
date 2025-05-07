// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function() {
    // Get the current page path
    const path = window.location.pathname;
    
    // Highlight the active navigation link
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === path) {
            link.classList.add('active');
        }
    });
    
    // Handle form validation
    const calculatorForm = document.getElementById('calculator-form');
    if (calculatorForm) {
        calculatorForm.addEventListener('submit', function(event) {
            if (!calculatorForm.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            calculatorForm.classList.add('was-validated');
        });
    }
    
    // Initialize the emissions chart on the results page
    const chartCanvas = document.getElementById('emissions-chart');
    if (chartCanvas) {
        const transportPercent = parseInt(chartCanvas.getAttribute('data-transport'));
        const homePercent = parseInt(chartCanvas.getAttribute('data-home'));
        const foodPercent = parseInt(chartCanvas.getAttribute('data-food'));
        
        new Chart(chartCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Transportation', 'Home Energy', 'Food & Consumption'],
                datasets: [{
                    data: [transportPercent, homePercent, foodPercent],
                    backgroundColor: [
                        '#20c997', // teal
                        '#fd7e14', // orange
                        '#6f42c1'  // purple
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Helper tooltips initialization
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});
