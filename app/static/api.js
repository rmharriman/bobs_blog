/**
 * Created by rmharriman on 12/21/16.
 */
function Menu(elem) {
    this.onUsers = function() {
        var request = new XMLHttpRequest();
        request.open('GET', 'http://localhost:5000/api/v1.0/posts/1', true);
        request.setRequestHeader("Authorization", "Basic" + btoa("rmharriman@gmail.com:cat"));
        request.onload = function() {
            if (this.status >= 200 && this.status < 400) {
                // Success!
                var data = JSON.parse(this.response);
                console.log(data);
                console.log("in success block");
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

new Menu(document.getElementById('menu'));