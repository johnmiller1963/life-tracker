M.AutoInit();
$(document).ready(function() {
    $('input#new_item_title, textarea#new_item_description').characterCounter();
    $('.datepicker').datepicker({'format': 'yyyy-mm-dd'});
});
