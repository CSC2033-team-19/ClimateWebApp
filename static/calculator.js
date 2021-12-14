$(function() {
    // get the range slider element.
    let electricity_factor_input = document.getElementById("clean_electricity_factor");

    // initialise tooltip for electricity factor input
    let electricity_factor_input_tooltip = new bootstrap.Tooltip(electricity_factor_input);

    // set up the default value
    electricity_factor_input.setAttribute("data-bs-original-title", electricity_factor_input.value + "%");

    // Add event listener for clean electricity update
    electricity_factor_input.addEventListener("input", (_) => {
        electricity_factor_input.setAttribute("data-bs-original-title", electricity_factor_input.value + "%");
        electricity_factor_input_tooltip.show();
    });

    // close the tooltip when the mouse leaves the slider
    electricity_factor_input.addEventListener("mouseleave", (_) => {
        electricity_factor_input_tooltip.hide();
    })


    // Add a listener for when the submit tab is opened
    $("#submit-tab, #other button.btn-next").click((event) => {
        // Set up variables for function
        var emission_values = {}
        const vehicle_type = $("#vehicle_type")

        // Select either the placeholder or value for each input in the page.
        document.querySelectorAll(".input-container input").forEach((element) => {
            emission_values[element.id] = element.value && !isNaN(element.value) ? element.value : element.placeholder;
        });

        // Ensure that a valid vehicle type is chosen, if somehow one is not chosen then default to other.
        emission_values["vehicle_type"] = vehicle_type.value ? vehicle_type.value : "Other";

        // Get the emission values from the costs given, and pass them to the chart.
        $.ajax({
            url: "/calculator/preview_values.json",
            type: "get",
            data: emission_values,
            success: create_chart
        })
    });


    // Set up buttons to change which tab is active
    $(".btn-next").click((event) => {
        $(".nav-item:has(a.active)").next("li").find("a").tab("show");
    });

    $(".btn-prev").click((event) => {
        $(".nav-item:has(a.active)").prev("li").find("a").tab("show");
    })
})

// Create dummy chart so that the program can regenerate a new chart each time the data is changed.
let preview_data_chart = new Chart();
function create_chart(result) {
    // Get the context for the chart.
    const ctx = document.getElementById("preview-chart").getContext('2d');

    // Destroy chart so that the new chart can be created in its place.
    preview_data_chart.destroy();

    // Create new chart with the data from the last page.
    preview_data_chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Travel', 'Home Utilities', 'Food Shopping', 'Other Expenses', "Total Emissions"],
            datasets: [{
                labels: ['Travel', 'Home Utilities', 'Food Shopping', 'Other Expenses', "Total Emissions"],
                data: [result.travel, result.home, result.food, result.other, result.total],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(75, 192, 192, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    })
}
