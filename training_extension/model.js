
var AllGames = Backbone.Collection.extend({
  model: NFLGame,

  url: 'http://127.0.0.1:5000/nflgames/',

  parse: function (response) {
    // Called on response from server
    $.each( response, function (idx, elem) {
      response[idx] = NFLGame.fromJSON(elem);
    });
    return response;
  }
});


var BlockedGames = Backbone.Collection.extend({
  model: Game,

  initialize: function () {
    // this.bind("add change remove", this.updateBackground, this);
  },

  pluckIds: function () {
    return this.map( function (elem) { return elem.id });
  }

});


var Game = Backbone.Model.extend({
  initialize: function (id, start, team1, team2, loc, score) {
    this.id = id;
    this.start = start;
    this.team1 = team1;
    this.team2 = team2;
    this.loc = loc;
    this.score = score;
  },
  toString: function () {
        return this.team1 + " vs " + this.team2;
    }
},{
  // Static methods
  fromJSON: function (jsono) {
    if (jsono.id && jsono.start && 
            jsono.team1 && jsono.team2 && 
            jsono.loc) {

        var t1 = jsono.team1;
        t1 = new Team.fromJSON(t1);
        var t2 = jsono.team2;
        t2 = new Team.fromJSON(t2);

        return new Game(jsono.id, jsono.start, t1, t2, jsono.loc, jsono.score);
    }
    console.log(jsono);
    throw "Bad json";
  }
});


var NFLGame = Game.extend({
  initialize: function (id, week, start, team1, team2, loc, score) {
    NFLGame.__super__.initialize.call(this, id, start, team1, team2, loc, score);
    this.week = week;
  },
  toString: function () {
    return "Week " + this.week + ": " + NFLGame.__super__.toString.call(this);
  }
},{
  // Static methods
  fromJSON: function (jsono) {
    if (jsono.id && jsono.week && jsono.start && 
        jsono.team1 && jsono.team2 && jsono.loc) 
    {
        var t1 = jsono.team1;
        t1 = new Team.fromJSON(t1);
        var t2 = jsono.team2;
        t2 = new Team.fromJSON(t2);

        return new NFLGame(jsono.id, jsono.week, jsono.start, t1, t2, jsono.loc, jsono.score);
    }
    console.log(jsono);
    throw "Bad json";
  }
});


var Team = Backbone.Model.extend({
  initialize: function (id, loc, name) {
    this.id = id;
    this.loc = loc;
    this.name = name;
  },
  toString: function () {
    return this.loc + " " + this.name;
  }
},{
  // Static methods
  fromJSON: function (jsono) {
    if (jsono.id && jsono.loc && jsono.name) {
        return new Team(jsono.id, jsono.loc, jsono.name);
    }
    throw "Bad json";
  }
});

var MessageStatuses = {
  OK: "okay",
  WARNING: "warning",
  ERROR: "error",
  fromStr: function (s) {
    s = s.toLowerCase();
    if (s == "ok" || s == "okay") return MessageStatuses.OK;
    if (s == "warning") return MessageStatuses.WARNING;
    if (s == "error") return MessageStatuses.ERROR;
    console.log("s is not a status. s:", s);
    return false;
  }
};


var Message = Backbone.Model.extend({
  defaults: {
    message: "",
    status: MessageStatuses.OK
  },

  initialize: function (options) {
    this.message = options.message;
    if (MessageStatuses.fromStr(options.status)) {
      this.status = options.status;
    } else {
      throw "status must be a MessageStatuses";
    }
  }
});

var MessagesList = Backbone.Collection.extend({
  model: Message
});


