$(document).ready(function() {
	$(".forms").hide();
	$(".createForm").hide();
	$(".joinForm").hide();

	$("#createBtn").click(function() {
		$(".forms").show();
		$(".joinForm").hide();
		$(".createForm").toggle(1000);
		$(".createForm").css("font-family" "Trebuchet MS, Helvetica, sans-serif");
	});

	$("#joinBtn").click(function() {
		$(".forms").show();
		$(".createForm").hide();
		$(".joinForm").toggle(1000)
		$(".joinForm").css("font-family" "Trebuchet MS, Helvetica, sans-serif");
	});
});