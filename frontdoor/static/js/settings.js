$(document).ready(function() {
	$("#formcont").load("../account-settings/");
	$(".home").css("visibility", "hidden");
	$(".settings").css("visibility", "visible");

	$(".accountset").click(function() {
		$("#formcont").load("../account-settings/");
		$(".navbtn").removeClass("active");
		$(this).addClass("active");
	});

	$(".homeset").click(function() {
		$("#formcont").load("../house-settings/");
		$(".navbtn").removeClass("active");
		$(this).addClass("active");
	});
});