var mouse_inside = false;

$('.nav .nav-pills li').click(function(){
	$(".nav .nav-pills li").removeClass("active");
	$(this).addClass("active");
})

$(document).ready(function(){
    $(".nav-pills a").click(function(){
        $(this).tabs('show');
    });

    $('.dropdown-toggle').dropdown();

    $('.totop').scrollTop(0);
});