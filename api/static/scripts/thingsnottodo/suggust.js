async function go(){
    var sugguestion = document.getElementById("what").value;
    const response = await fetch('/thingsnottodo/sugguest', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({"sugguestion":sugguestion})
    });
    const data = await response.json();
    document.getElementById("id").innerHTML = "Your sugguestion ID: " + data.id + "<br><a href=\"/thingsnottodo/check?id=" + data.id + ">View it here</a>"
}