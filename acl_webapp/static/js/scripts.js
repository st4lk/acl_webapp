(function($)  {
    'use strict'

    var AJAX_LOADER_SMALL = "/static/img/loading_small.gif"
    var ERR_CLASSES = ["has-error"];

    // String.format method.
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

    function ajax_amin_small(cls){
        return $("<img class='{0}' src='{1}'/>".format(
            cls, AJAX_LOADER_SMALL));
    }

    function clearErr(frm){
        var frm_field_wrapper = frm.find('.form-group');
        for (var i=0; i<frm_field_wrapper.length; i++){
            for (var j=0; j<ERR_CLASSES.length; j++){
                $(frm_field_wrapper[i]).removeClass(ERR_CLASSES[j]);
            }
            frm.find('p.help-block').remove();
        }
    }

    function showRequest(formData, jqForm, options) { 
        // start animation
        var loader_small = ajax_amin_small('reg_post_anim');
        $(".modal-footer").prepend(loader_small);
        $("#register_submit").attr('disabled', 'disabled');
        return true; 
    } 


    function showResponse(responseText, statusText, xhr, $form) {
        // stop animation
        $('.reg_post_anim').remove();
        $("#register_submit").removeAttr('disabled');
        // process response
        var resp = responseText;
        var frm = $("#register_ajax_form");
        clearErr(frm);
        if (resp.result){
            window.location.replace(resp.redirect_url);
        } else {
            //show errors
            var cnt = 1;
            for (var err in resp.errors){
                var fail_elem = frm.find('#' + err);
                var fail_group = fail_elem.closest(".form-group");
                for (var j=0; j<ERR_CLASSES.length; j++){
                    fail_group.addClass(ERR_CLASSES[j]);
                }
                fail_group.append('<p class="help-block"><strong>{0}</strong></p>'.format(
                    resp.errors[err]
                ))
                cnt += 1;
            }
        }
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
        var loader_small = ajax_amin_small('reg_btn_anim');
        return this.each(function(){
            $(this).click(function(){
                var btn = $(this);
                var modal_elem = $("#register_modal");
                if (modal_elem.length == 0){
                    loader_small.insertAfter(btn);
                    btn.addClass('disabled');
                    $.get(btn.attr('href'), function(data){
                        $(data).appendTo('body');
                        modal_elem = $("#register_modal");
                        modal_elem.ajax_register();
                        modal_elem.modal();
                        btn.removeClass('disabled');
                        loader_small.remove();
                    });
                } else {
                    modal_elem.modal('toggle');
                }
                return false;
            })
        })
    }

})(jQuery);

