$(function () {
    // initialise date picker
    $.datepicker.regional['uk'] = {
        dateFormat: "dd-mm-yy"
    }

    $.datepicker.setDefaults(
        $.datepicker.regional['uk']
    )

    $("#date").datepicker();
})