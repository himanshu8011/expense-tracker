function confirmDelete() {
    return confirm("Are you sure you want to delete this expense?");
}
function toggleDark() {
    document.body.classList.toggle("dark");
}
// optional future scripts
console.log("Expense Tracker Loaded");
const data = window.categoriesData;

new Chart(document.getElementById('chart'), {
    type: 'pie',
    data: {
        labels: Object.keys(data),
        datasets: [{
            data: Object.values(data)
        }]
    }
});