(function($)  {
  'use strict'
    // First, checks if it isn't implemented yet.
    if (!String.prototype.format) {
        String.prototype.format = function() {
          var args = arguments;
          return this.replace(/{(\d+)}/g, function(match, number) {
            return typeof args[number] != 'undefined'
              ? args[number]
              : match
            ;
          });
        };
    }

    function showRequest(formData, jqForm, options) { 
        console.log("requesting...");
        return true; 
    } 


    function showResponse(responseText, statusText, xhr, $form)  {
        console.log("response:");
        console.log(resp);
    } 

    $.fn.ajax_register = function(){
        // require <script src="http://malsup.github.com/jquery.form.js"></script>
        var options = { 
            beforeSubmit:  showRequest,
            success:       showResponse
        };
        return this.each(function() {
            $(this).ajaxForm(options);
            return false;
          })
    }

    $.fn.show_register_form = function(){
        // suggestion modal form
        // var loader_small = $("<img class='ajax-loader-small pull-right get-msg-frm-loader' src='/static/img/loading_small.gif'/>");
        return this.each(function(){
            $(this).click(function(){
                var btn = $(this);
                var modal_elem = $("#register_modal");
                if (modal_elem.length == 0){
                    // loader_small.insertAfter(btn);
                    btn.addClass('disabled');
                    $.get(btn.attr('href'), function(data){
                        console.log(data);
                        $(data).appendTo('body');
                        modal_elem = $("#register_modal");
                        modal_elem.ajax_register();
                        modal_elem.modal();
                        btn.removeClass('disabled');
                        // loader_small.hide();
                    });
                } else {
                    modal_elem.modal('toggle');
                }
                return false;
            })
        })
    }

})(jQuery);

