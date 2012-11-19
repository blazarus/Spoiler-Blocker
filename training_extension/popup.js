$(function () {
  console.log("this is working");


  // events = [] //populate this with AJAX call with Event objects
  // for (var i = 0, evnt; evnt = events[i], i++) {

  // }
  // $("#events-dropdown").append()

  $.getJSON('http://127.0.0.1:5000/events/', function (data) {
  	console.log(data);
  	var elem = $("select#events-dropdown");
  	for (var i = 0, eventJSON; eventJSON = data[i]; i++) {
  		console.log("event:", eventJSON);
  		var evt = Event.prototype.fromJSON(eventJSON);

  		var newElem = $("<option>").attr("value", evt.id).text(evt);
			elem.append(newElem);
  	}
  });

  chrome.tabs.executeScript(null, { file: "jquery-1.8.2.min.js" }, function() {
    chrome.tabs.executeScript(null, { file: "contentscript.js" });
    chrome.extension.onRequest.addListener( function (data, sender, sendResponse) {
    	console.log("ok got message back from content script! in popup");
    	// console.log("data:", $(data));
    	// $(data).not("script").each( function (idx, elem) {
    	// 	console.log(idx, elem, $(elem).text());
    	// });
    	// console.log("text:", text);
    	$("input#content").val(data.content)
    	$("input#url").val(data.url)
    });
  }); 
});

var Event = function (id, start, team1, team2, loc, score) {
	if (!this instanceof Event) return new Event(id, start, team1, team2, loc, score);

	this.id = id;
	this.start = start;
	this.team1 = team1;
	this.team2 = team2;
	this.loc = loc;
	this.score = score;

	this.toString = function () {
		return this.team1 + " vs " + this.team2;
	}
}

Event.prototype.fromJSON = function (jsono) {
	if (jsono.id && jsono.start && 
			jsono.team1 && jsono.team2 && 
			jsono.loc) {

		var t1 = jsono.team1;
		t1 = new Team.prototype.fromJSON(t1);
		var t2 = jsono.team2;
		t2 = new Team.prototype.fromJSON(t2);

		return new Event(jsono.id, jsono.start, t1, t2, jsono.loc, jsono.score);
	}
	console.log(jsono);
	throw "Bad json";
}

var Team = function (id, loc, name) {
	if (!this instanceof Team) return new Team(id, loc, name);

	this.id = id;
	this.loc = loc;
	this.name = name;

	this.toString = function () {
		return this.loc + " " + this.name;
	}
}

Team.prototype.fromJSON = function (jsono) {
	if (jsono.id && jsono.loc && jsono.name) {
		return new Team(jsono.id, jsono.loc, jsono.name);
	}
	throw "Bad json";
}

