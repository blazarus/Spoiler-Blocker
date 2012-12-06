var pageContent, pageUrl, games, blockedGames, 
    gamesListView, blockedGamesView, 
    messagesList, messagesListView;

$(function () {
  // Collections
  games = new AllGames();
  blockedGames = new BlockedGames();
  messagesList = new MessagesList();
  // Views
  // Note: right now I'm passing in blockedGames to gamesListView - should set up a 
  // central event dispatcher so I don't have that dependency
  messagesListView = new MessagesListView({ collection: messagesList });
  gamesListView = new GamesListView({ 
    collection: games, 
    blockedGames: blockedGames
  });
  blockedGamesView = new BlockedGamesView({ collection: blockedGames });

  games.fetch({success: function () {
    console.log("Successfully fetched games from server:", games);
    gamesListView.render();
    
  }});

  for (var i = 1; i < 18; i++) {
    var opt = $("<option>").attr("val", i).text(i);
    $("#pick-week").append(opt);
  }
  $("#pick-week").change( function (e) {
    // clear the list
    $("#games-list").html();

    $.each(games.models, function (idx, game) {
      if (game.week == $("#pick-week").val()) {
        var elem = $("<li>").text(game).prepend("<input type=checkbox>");
        $("#game-list").append(elem);
      }
    });
  });
  

  $("form#vote-form").submit( function (e) {
    e.preventDefault();

    if (!pageUrl || !pageContent) {
      // Page may have been refreshed while popup was open,
      // so need to get page info again.
      // Then Post vote to server
      console.log("Retrieving page info before posting vote.");
      getPageInfo(postVote);
    } else {
      // Otherwise just post the vote
      postVote();
    }

    
  });

  // Once popup is opened, execute content script to
  // get html of the web page currently being viewed
  getPageInfo();
});

var getPageInfo = function (callback) {
  chrome.tabs.executeScript(null, { file: "jquery-1.8.2.min.js" }, function() {
    chrome.tabs.executeScript(null, { file: "contentscript.js" });
    chrome.extension.onRequest.addListener( function (data, sender, sendResponse) {
        console.log("ok got message back from content script! in popup:", data);
        // console.log("data:", $(data));
        // $(data).not("script").each( function (idx, elem) {
        //  console.log(idx, elem, $(elem).text());
        // });
        // console.log("text:", text);
        if (!data.url || !data.content) alert("Something went wrong getting page info from content script.");

        pageUrl = data.url;
        pageContent = data.content;
        // $("input#content").val(data.content)
        // $("input#url").val(data.url)

        if (callback) callback();
    });
  }); 
}

var postVote = function () {
  var url = "http://127.0.0.1:5000/vote";

  var vote = $("input[type='radio']:checked").val();
  vote  = vote.toLowerCase() == "yes" ? true : false;

  if (blockedGames.pluckIds().length == 0) {
    alert("Need to chose 1 or more events to vote for.");
    return;
  }

  $("#game-list li input:checked").parent();

  var data = {
    gameIds: blockedGames.pluckIds().toString(),
    content: pageContent,
    url: pageUrl,
    vote: vote
  };
  $.post(url, data, function (response) {
    console.log("Posted vote to server, got response:", response);
    response = $.parseJSON(response);

    if (!response.status || !MessageStatuses.fromStr(response.status)) {
      alert("Server did not return a recognized response message.");
      return;
    }

    var status = MessageStatuses.fromStr(response.status);
    var message = "";
    if (response.message) message = response.message;

    if (status == MessageStatuses.OK || status == MessageStatuses.WARNING) {
      blockedGames.reset();
      blockedGamesView.render();
      gamesListView.render();
    } 
    console.log("message:", message);
    messagesList.add(new Message({message: message, status: status}));
  });
}
