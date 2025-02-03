async function go(){
    var sugguestion = document.getElementById("id").value;
    const response = await fetch('/thingsnottodo/suggest', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({"sugguestion" : sugguestion})
    });
    const data = await response.json();
    if(data.error){
        alert("Error: " + data.error)
        return;
    }
    document.getElementById("idview").innerHTML = "Your sugguestion ID: " + data.id;
    document.getElementById("view").setAttribute("href", "/thingsnottodo/check?id=" + data.id);
    document.getElementById("view").removeAttribute("hidden");
}