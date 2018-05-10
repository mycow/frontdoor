$(document).ready(function() {
	$(".heading").append("<h2>Account Settings</h2>");
	$("#formcont").load("../account-settings/");
	$(".home").css("visibility", "hidden");
	$(".settings").css("visibility", "visible");

	$(".accountset").click(function() {
		$(".heading").empty();
		$(".heading").append("<h2>Account Settings</h2>");
		$("#formcont").load("../account-settings/");
		$(".navbtn").removeClass("active");
		$(this).addClass("active");
	});

	$(".homeset").click(function() {
		$(".heading").empty();
		$(".heading").append("<h2>House Settings</h2>");
		$("#formcont").load("../house-settings/ #setForm");
		$(".navbtn").removeClass("active");
		$(this).addClass("active");
	});
});