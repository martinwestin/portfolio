
String.prototype.format = function() {
    a = this;
    for (k in arguments) {
        a = a.replace("{" + k + "}", arguments[k]);
    }
    return a;
}

var socket;
$(document).ready(function() {
    socket = io.connect("/");
    const chat = $(".chat-content");
    chat.scrollTop(chat.prop("scrollHeight"));

    socket.on("connect", function() {
        const url = window.location.href;
        const user = url.split("/").pop().split("?")[0];

        socket.emit("connected_dm", {
            _with: user 
        });
    })

    socket.on("new_message", function(msg) {
        const sender = msg["sender"];
        const published = msg["published"];
        const content = msg["content"];

        let newInnerHTML = chat.html();
        newInnerHTML += "<div class='message'><p>{0} | {1} <br> {2}</p></div>".format(sender, published, content);
        chat.html(newInnerHTML);
        chat.scrollTop(chat.prop("scrollHeight"));
    })

    $("#send-input").bind("keyup", function(event) {
        if (event.keyCode === 13) {
            socket.emit("new_message", {
                data: $("#send-input").val()
            });
            $("#send-input").val("");
        }
    })
})