
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
    $("#submit-tab").click((event) => {
        var emission_values = {}
        document.querySelectorAll(".input-container input").forEach((element) => {
            emission_values[element.id] = element.value && !isNaN(element.value) ? element.value : element.placeholder;
        });
        var vehicle_type = $("#vehicle_type")
        emission_values["vehicle_type"] = vehicle_type.value ? vehicle_type.value : "Other";

        $.ajax({
            url: "/calculator/preview_values.json",
            type: "get",
            data: emission_values,
            success: (result) => {
                console.log(result);
            }
        })
    })
})

