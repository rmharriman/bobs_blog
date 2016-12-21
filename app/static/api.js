/**
 * Created by rmharriman on 12/21/16.
 */

var token;

function buildTable(userList) {
    var table = document.createElement("table");
    var header = table.createTHead();
    var row = header.insertRow(0);
    var cell = row.insertCell(0);
    cell.innerHTML = "Users";

    for (var user of userList) {
        var userRow = table.insertRow(-1);
        var userData = userRow.insertCell(0);
        userData.innerHTML = user.username;
    }
    return table;
}

function Menu(elem) {
    this.onUsers = function() {
        var request = new XMLHttpRequest();
        request.open('GET', 'http://localhost:5000/api/v1.0/users/', true);
        if (!token) {
            alert("Please get a token first");
            return false;
        }
        request.setRequestHeader("Authorization", "Basic " + btoa(token + ":"));
        request.onload = function() {
            if (this.status >= 200 && this.status < 400) {
                // Success!
                var data = JSON.parse(this.response);
                var tableDiv = document.getElementById("users");
                tableDiv.appendChild(buildTable(data.users));

            }
            else {
            // We reached our target server, but it returned an error
            }
        };

        request.onerror = function() {
        // There was a connection error of some sort
        };

        request.send();
    };

    this.onToken = function() {
        var request = new XMLHttpRequest();
        request.open('GET', 'http://localhost:5000/api/v1.0/token', true);
        request.setRequestHeader("Authorization", "Basic " + btoa("rmharriman@gmail.com:cat"));
        request.onload = function() {
            if (this.status >= 200 && this.status < 400) {
                // Success!
                var data = JSON.parse(this.response);
                console.log(data);
                token = data.token

            }
            else {
            // We reached our target server, but it returned an error
            }
        };

        request.onerror = function() {
        // There was a connection error of some sort
        };

        request.send();
    };

    this.onPosts = function() {
        alert('loading');
    };

    var self = this;

    elem.onclick = function(e) {
        var target = e.target;
        // lookup function to get data (getData(Action)
        var action = target.getAttribute('data-action');
        if (action) {
            self["on"+action]();
        }
    }
}

var myMenu = new Menu(document.getElementById('menu'));