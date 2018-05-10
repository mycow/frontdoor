var mouse_inside = false;

$('.nav .nav-tabs li').click(function(){
	$(".nav .nav-tabs li").removeClass("active");
	$(this).addClass("active");
})

$(document).ready(function(){
	$(".feed").addClass("active");

    $(".nav-tabs a").click(function(){
        $(this).tabs("option", "show");
    });

    $('.dropdown-toggle').dropdown();

    $('.totop').scrollTop(0);
});