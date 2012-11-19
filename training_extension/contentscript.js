data = {}

data.content = $("html").html()
data.url = window.location.href
// console.log(data)

// console.log($("p"))
// $("p").css({
// 	'border': '10px solid red'
// });

// $(document).on('mouseover', "p, a, li", function(e) {
// 	// console.log(this.nodeType);
// 	$(this).css("background-color","yellow");
// );
// $(document).on('mouseout', "p, a, li", function(e) {
// 	$(this).css("background-color","transparent");
// });

chrome.extension.sendRequest(data, function () {
	console.log("sent request");
});
