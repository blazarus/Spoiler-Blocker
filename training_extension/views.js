var NFLGameView = Backbone.View.extend({
	tagName:  "li",

    initialize: function () {
    	this.model.view = this;
    },

	render: function () {
  		var e = this.$el;
		e.html(this.model.toString());
		e.attr("id",this.model.id);
		e.append("<a class='remove' href='' title='Remove'>x</a>")
		return this;
	}
});

var GamesListView = Backbone.View.extend({
	el: "#events-dropdown",

	events: {
		"change" : "select"
	},

	initialize: function () {
		this.collection.view = this;
		this.options.blockedGames.bind("add change remove reset", this.render, this);
	},

	render: function () {
		console.log("Rendering GamesListView with games:", this.collection);

		// First clear view
		this.$el.html("");

		// Add back default option
		this.$el.append('<option value="" id="default-option" disabled>Select events to vote for</option>');
		this.$el.prop('selectedIndex', 0); // Set select to default option

		// Now populate the list
		var that = this;
		$.each(this.collection.models, function (idx, elem) {
			var newElem = $("<option>").attr("id", elem.id).attr("value", elem.id).text(elem);
        	that.$el.append(newElem);
		});

		$.each(that.options.blockedGames.models, function (idx, game) {
			that.$("option#" + game.id).attr("disabled", "");
		});
	},

	select: function (e) {
	    var selected = this.$el.val();
	    var game = this.collection.get(selected);
	    
	    this.options.blockedGames.add(game);

	    this.$("option#" + game.id).attr("disabled", "");
	    console.log("added to blockedgames:", this.options.blockedGames);
	}
});

var BlockedGamesView = Backbone.View.extend({
	el: "ul#blocked-events",

	events: {
		"click .remove" : "removeBlockedGame"
	},

	initialize: function () {
		this.collection.view = this;

		this.collection.bind("add change remove", this.render, this);
	},

	render: function () {
		console.log("Rendering blockedGamesView");
		var that = this;
		this.$el.html("");
		$.each(this.collection.models, function (idx, elem) {
			var gameView = new NFLGameView({ model: elem });
		    that.$el.append(gameView.render().$el);
		});
		if (this.collection.models.length != 0) {
			this.$el.append("<hr />");
		}
	},

	removeBlockedGame: function (e) {
		e.preventDefault();
		var gameId = $(e.target).parent().attr("id")
	    // Remove from blocked list, remove element, enable option in dropdown
	    this.collection.remove(gameId); //Remove event from blocked elements array

	    $("#events-dropdown option#" + gameId).removeAttr("disabled");

	    console.log("blocked events:", this.collection);
	}
});

var MessagesListView = Backbone.View.extend({
	el: "#message-container",

	initialize: function () {
		this.collection.bind("add", function (e) {
			this.addMessage(e);
		}, this);
	},

	render: function () {
		$.each(this.collection.models, function (idx, msg) {
			addMessage(msg)
		});
	},

	addMessage: function (msg) {
		var that = this;
		var messageDiv = $("<li class='message'>").addClass(msg.status)
						.append($("<span>").html(msg.message));

		var closeButton = $('<a href="" id="close">Close</a>')
			.click( function (e) {
				e.preventDefault();
				messageDiv.fadeOut("slow");
				that.collection.remove(msg);
			});

		var remove = function (messDiv, that) {
			// form a closure to seal in the value of messDiv
			return (function () { 
				messDiv.fadeOut("slow"); 
				that.collection.remove(msg);
			});
		};
		setTimeout(remove(messageDiv, that), 15000);

		messageDiv.append(closeButton);
		that.$el.append(messageDiv);
	}
});



