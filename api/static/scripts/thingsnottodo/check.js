function getQueryVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split("=");
        if (pair[0] == variable) {
            return pair[1];
        }
    }
    return "";
}
id = getQueryVariable("id")
async function init() {
    if (id != "") {
        const response = await fetch('/thingsnottodo/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "id" : id })
        });
        const data = await response.json();
        if (data.error) {
            alert("Error: " + data.error);
            return;
        }
        document.getElementById("status").removeAttribute("hidden");
        document.getElementById("main").innerHTML = data.status;
    }
}
init();