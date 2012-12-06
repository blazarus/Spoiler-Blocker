data = {}

data.content = $("html").html()
data.url = window.location.href


chrome.extension.sendRequest(data, function () {
	console.log("sent request");
});
