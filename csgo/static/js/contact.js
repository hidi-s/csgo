
$(document).ready(function(){
    $('#contact_submit').unbind().bind('click', function(){
        sendAjaxForm();
    });
});
function sendAjaxForm(){
    var formData = $('#contact-us-form').serializeArray();
    console.log(formData);
    $.ajax({
        url: "contact_us.php",
        data: formData,
        type: "POST",
        dataType: "json",
        context: document.body,
        beforeSend: function(){
            $('#contact_submit').attr('disabled', true);
        },
        success: function(data){
            $('#error_placeholder').empty();
            if(data.message){
                $('#error_placeholder').append(data.message);
            }
            $('#contact_submit').attr("disabled", false);
        }

    });
}