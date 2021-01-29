// First line auto initialises all Materialize components
M.AutoInit();
$(document).ready(function() {
    $('input#new_item_title, textarea#new_item_description').characterCounter();
    $('.datepicker').datepicker({'format': 'yyyy-mm-dd'});
    // $('.datepicker').setDefaults({ beforeShow: function (i) { if ($(i).attr('readonly')) { return false; } } });
    if ($('.datepicker').prop('readonly')) {
        $('#ui-datepicker-div').css({ 'visibility': 'hidden' })
    } else { $('#ui-datepicker-div').css({ 'visibility': 'visible' }) }
});
