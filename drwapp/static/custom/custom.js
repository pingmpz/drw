remove_valids = (input_ids) => { for(var i = 0;i < input_ids.length;i++) remove_valid(input_ids[i]); }
valids = (input_ids) => { for(var i = 0;i < input_ids.length;i++) valid(input_ids[i]); }
invalids = (input_ids) => { for(var i = 0;i < input_ids.length;i++) invalid(input_ids[i]); }
hides = (input_ids) => { for(var i = 0;i < input_ids.length;i++) hide(input_ids[i]); }
unhides = (input_ids) => { for(var i = 0;i < input_ids.length;i++) unhide(input_ids[i]); }
set_input_emptys = (input_ids) => { for(var i = 0;i < input_ids.length;i++) set_input_empty(input_ids[i]); }
set_input_zeros = (input_ids) => { for(var i = 0;i < input_ids.length;i++) set_input_zero(input_ids[i]); }
set_text_emptys = (input_ids) => { for(var i = 0;i < input_ids.length;i++) set_text_empty(input_ids[i]); }

function remove_valid(input_id){
  $("#"+input_id).removeClass("is-invalid");
  $("#"+input_id).removeClass("is-valid");
}

function valid(input_id){
  $("#"+input_id).addClass("is-valid");
  $("#"+input_id).removeClass("is-invalid");
}

function invalid(input_id){
  $("#"+input_id).addClass("is-invalid");
  $("#"+input_id).removeClass("is-valid");
}

function hide(input_id){
  $("#"+input_id).prop("hidden", true);
}

function unhide(input_id){
  $("#"+input_id).prop("hidden", false);
}

function set_input_empty(input_id){
  $("#"+input_id).val("");
}

function set_input_zero(input_id){
  $("#"+input_id).val("0");
}

function set_text_empty(input_id){
  $("#"+input_id).text("");
}

function set_text_value(input_id, value){
  $("#"+input_id).text(value);
}
