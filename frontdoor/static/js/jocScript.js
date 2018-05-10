$(document).ready(function() {
	$(".forms").hide();
	$(".createForm").hide();
	$(".joinForm").hide();

	$("#createBtn").click(function() {
		$(".forms").show();
		$(".joinForm").hide();
		$(".createForm").toggle(1000);
	});

	$("#joinBtn").click(function() {
		$(".forms").show();
		$(".createForm").hide();
		$(".joinForm").toggle(1000);
	});
});