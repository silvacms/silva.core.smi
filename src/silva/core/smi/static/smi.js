// SMI Javascript

$(document).ready(function() {
    var baseurl = $('#smi-content-url').attr('href');

    // Add new content auto submit
    $('#md-container-field-content').bind('change', function() {
        $('#md-container-action-new').trigger('click');
    });
    $(document).bind('zeam-popup-closed', function() {
        $.getJSON(baseurl + '/++rest++smi-feedback', function(data) {
            $('#feedback').replaceWith(data['messages']);
        });
    });
});
