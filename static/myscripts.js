//rendering dropdown menu select


$(".dropdown-menu li a").click(function(){
	alert("aaa");
  var selText = $(this).text();
  $(this).parents('.form-group').find('button[data-toggle="dropdown"]').html(selText+' <span class="caret"></span>');
});