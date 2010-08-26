
$(document).ready(function() {
    // Add new content
    $('#md-container-field-content').change(function() {
        $('#md-container-action-new').trigger('click');
    });
    // Focus first required field
    $('.zeam-form .field-required:first').trigger('focus');
});
