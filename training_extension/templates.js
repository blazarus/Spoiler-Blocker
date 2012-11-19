var Templates = new function () {
	this.eventSelectTemplate = '\
		<option value="<%= event.id %>"><%= event.toString() %></option>';
}();