String.prototype.format = function() {
    a = this;
    for (k in arguments) {
        a = a.replace("{" + k + "}", arguments[k]);
    }
    return a;
}

class PopupBox {
    constructor(content=null) {
        this.content = content
    }
    
    config(content) {
        this.content = content
    }

    show() {
        document.getElementById("bg-mask").style.visibility = "visible";
        document.getElementById("popup-box").style.visibility = "visible";
        $("#popup-content").html("");
        let newInnerHTML = $("#popup-content").html();
        newInnerHTML += "<p>{0}</p>".format(this.content);
        $("#popup-content").html(newInnerHTML);
    }

    hide() {
        document.getElementById("bg-mask").style.visibility = "hidden";
        document.getElementById("popup-box").style.visibility = "hidden";
    }
}

function showElement(elementId) {
    document.getElementById(elementId).style.visibility = "visible";
}

let popup = new PopupBox();

var socket;
let topicsArray = ['AWS', 'AngularJS', 'Back-end programming', 'C', 'C#', 'C++', 'CSS', 'Django', 'Firebase', 'Flask', 'Front-end programming', 'Game Development', 'GoLang', 'HTML', 'Java', 'JavaScript', 'Kotlin', 'MongoDB', 'MySQL', 'Node.js', 'PHP', 'Perl', 'PostgreSQL', 'PowerShell', 'Python', 'Python 2', 'Python 3', 'R', 'React', 'Ruby', 'Rust', 'SQL', 'Scala', 'Swift', 'Unity', 'Unreal Engine', 'jQuery'];
let subjectsArray = ['Accounting', 'Aeronautical Engineering', 'Architecture', 'Art', 'Business', 'Computer Science & Information Systems', 'Design', 'Economics', 'Finance', 'Law', 'Management Studies', 'Manufacturing Engineering', 'Mechanical Engineering', 'Medicine']

$(document).ready(function() {
    const educationContainer = $(".education-container");
    educationContainer.scrollTop(educationContainer.prop("scrollHeight"));

    socket = io.connect("/");

    socket.on("reload", function() {
        location.reload();
    })

    socket.on("non_valid_file", function() {
        popup.config("This image file is not valid. It has to have one of the following extenstions: .jpg, .png, .jpeg, .gif");
        popup.show();
    })

    socket.on("has_already_added", function(msg) {
        popup.config("You have already added this {0}. You cannot add it again.".format(msg["type"]));
        popup.show()
    })

    socket.on("search_response", function(msg) {
        const results = msg["results"];
        const auto_complete_div = $("#users-auto-complete");
        auto_complete_div.html("");
        let newInnerHTML = auto_complete_div.html();
        // create table
        newInnerHTML += "<table><tr><th>First name</th><th>Last name</th><th>Username</th></tr>";

        for (const element in results) {
            newInnerHTML += "<tr><td>{0}</td><td>{1}</td><td><a href='/portfolio/{2}'>{3}</a></td></tr>".format(results[element][0], results[element][1], results[element][2], results[element][2]);
        }
        newInnerHTML += "</table>";
        auto_complete_div.html(newInnerHTML);
    })

    $("#submit-photo").click(function() {
        const selected = document.getElementById("photo-file").files[0];
        socket.emit("select_profile_pic", {
            img: selected,
            name: selected.name
        });
    })

    $("#save-introduction").click(function() {
        const val = $("#intro-text-box").val();
        socket.emit("save_user_introduction", {
            content: val
        });
    })
    let input = $("#new-merit");
    let newEducationTopic = $("#new-education-topic");
    let user_search = $("#search-user");
    const auto_complete_div = $("#merits-auto-complete");
    const subjects_auto_complete = $("#subjects-auto-complete");

    user_search.bind("keyup", function(event) {
        if (event.keyCode === 13) {
            socket.emit("user_search", {
                user: user_search.val()
            });
        }
    })

    input.bind("keyup", function(event) {
        showElement("merits-auto-complete");
        let newInnerHTML = "";
        if (input.val().length != 0) {
        
            let relevantOptions = autoComplete(topicsArray, input.val());
            for (const element in relevantOptions) {
                const option = relevantOptions[element];
                newInnerHTML += "<div class='option'><div class='option-name'><p>{0}</p></div>".format(option);
                newInnerHTML += "<div class='add-button-container'><button class='add-button' onclick='click_topic({0})'>Add</button></div>".format(topicsArray.indexOf(option));
                newInnerHTML += "</div>";
            }
            auto_complete_div.html(newInnerHTML);
        } else {
            for (const element in topicsArray) {
                const option = topicsArray[element];
                newInnerHTML += "<div class='option'><div class='option-name'><p>{0}</p></div>".format(option);
                newInnerHTML += "<div class='add-button-container'><button class='add-button' onclick='click_topic({0})'>Add</button></div>".format(topicsArray.indexOf(option));
                newInnerHTML += "</div>";
            }
            auto_complete_div.html(newInnerHTML);
        }
    })

    input.mousedown(function() {
        showElement("merits-auto-complete");
        if (input.val().length == 0) {
            auto_complete_div.html("");
            let newInnerHTML = "";
            for (const element in topicsArray) {
                const option = topicsArray[element];
                newInnerHTML += "<div class='option'><div class='option-name'><p>{0}</p></div>".format(option);
                newInnerHTML += "<div class='add-button-container'><button class='add-button' onclick='click_topic({0})'>Add</button></div>".format(topicsArray.indexOf(option));
                newInnerHTML += "</div>";
            }
            auto_complete_div.html(newInnerHTML);
        }
    })

    newEducationTopic.bind("keyup", function(event) {
        showElement("subjects-auto-complete");
        let newInnerHTML = "";

        if (newEducationTopic.val().length != 0) {
            let relevantOptions = autoComplete(subjectsArray, newEducationTopic.val());
            for (const element in relevantOptions) {
                const option = relevantOptions[element];
                newInnerHTML += "<div class='option'><div class='option-name'><p>{0}</p></div>".format(option);
                newInnerHTML += "<div class='add-button-container'><button class='add-button' onclick='clickEducationTopic({0})'>Add</button></div>".format(subjectsArray.indexOf(option));
                newInnerHTML += "</div>";
            }
            subjects_auto_complete.html(newInnerHTML);

        } else {
            for (const element in subjectsArray) {
                const option = subjectsArray[element];
                newInnerHTML += "<div class='option'><div class='option-name'><p>{0}</p></div>".format(option);
                newInnerHTML += "<div class='add-button-container'><button class='add-button' onclick='clickEducationTopic({0})'>Add</button></div>".format(subjectsArray.indexOf(option));
                newInnerHTML += "</div>";
            }
            subjects_auto_complete.html(newInnerHTML);
        }
    })

    newEducationTopic.mousedown(function() {
        showElement("subjects-auto-complete");
        if (newEducationTopic.val().length == 0) {
            subjects_auto_complete.html("");
            let newInnerHTML = "";
            
            for (const element in subjectsArray) {
                const option = subjectsArray[element];
                newInnerHTML += "<div class='option'><div class='option-name'><p>{0}</p></div>".format(option);
                newInnerHTML += "<div class='add-button-container'><button class='add-button' onclick='clickEducationTopic({0})'>Add</button></div>".format(subjectsArray.indexOf(option));
                newInnerHTML += "</div>";
            }
            subjects_auto_complete.html(newInnerHTML);
        }
    })


})

function autoComplete(options, value) {
    let relevant = [];
    for (const element in options) {
        if (options[element].toLowerCase() == value.toLowerCase() || options[element].toLowerCase().includes(value.toLowerCase())) {
            relevant.push(options[element]);
        }
    }
    return relevant;
}

function click_topic(index) {
    const topic = topicsArray[index];
    socket.emit("new_topic", {
        data: topic
    });
}

function clickEducationTopic(index) {
    const topic = subjectsArray[index];
    socket.emit("new_education_merit", {
        data: topic
    });
}

function changeLevel(type, topic, current) {
    // type --> improve or decrease.
    // -1 --> decrease, 1 --> improve
    socket.emit("change_level", {
        type: type,
        topic: topic,
        current: current
    });
}

function changeEducationLevel(type, topic, current) {
    // type --> improve or decrease.
    // -1 --> decrease, 1 --> improve
    socket.emit("change_education_level", {
        type: type,
        topic: topic,
        current: current
    });
}

function deleteMerit(topic) {
    socket.emit("delete_merit", {
        topic: topic
    });
}

function deleteEducationMerit(topic) {
    socket.emit("delete_education_merit", {
        topic: topic
    });
}
