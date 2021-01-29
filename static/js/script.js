// First line auto initialises all Materialize components
M.AutoInit();
$(document).ready(function() {
    // Character counters enabled for 'new item' only, not editing item, 
    // though max character limits are still in place
    $('input#new_item_title, textarea#new_item_description').characterCounter();
    $('.datepicker').datepicker({'format': 'yyyy-mm-dd'});
});
