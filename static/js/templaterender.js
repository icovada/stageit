$("#templaterender").on('show.bs.modal', function () {
    $('#templaterenderview').html("");
    $.ajax({
        type: "POST",
        url: "/api/convertjinja",
        data: {
            template: $('#template').val(),
            values: JSON.stringify($('#templatevalues').val())
        },
        success: function (msg) {
            $('#templaterenderview').html(msg);
        },
        error: function (msg, exception) {
            $('#templaterenderview').html(msg.responseText);
        }
    });
})