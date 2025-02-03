var submissionId = "[null]";
async function getNew(){
    const response = await fetch('/thingsnottodo/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({"type" : "get"})
    });
    const data = await response.json();
    if(data.error){
        alert("Error: " + data.error);
        return;
    }
    submissionId = data.id;
    document.getElementById("main").innerHTML = data.content;
    document.getElementById("verify").removeAttribute("hidden");
    document.getElementById("deny").removeAttribute("hidden");
    document.getElementById("softclear").removeAttribute("hidden");
    document.getElementById("fullclear").removeAttribute("hidden");
    document.getElementById("status").innerHTML = data.status;
    if (data.status == "ACCEPTED"){
        document.getElementById("main").setAttribute("style", "font-family: 'Courier New', Courier, monospace; color: green;");
    }
}
async function accept() {
    const response = await fetch('/thingsnottodo/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({"type" : "accept", "id" : submissionId})
    });
    const data = await response.json();
    if(data.error){
        alert("Error: " + data.error);
        return;
    }
}
async function deny() {
    const response = await fetch('/thingsnottodo/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({"type" : "deny", "id" : submissionId})
    });
    const data = await response.json();
    if(data.error){
        alert("Error: " + data.error);
        return;
    }
}
async function hardclear(){
    if(!confirm("Are you sure?")){
        return;
    }
    const response = await fetch('/thingsnottodo/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({"type" : "fullclear"})
    });
    const data = await response.json();
    if(data.error){
        alert("Error: " + data.error);
        return;
    }
}
async function softclear(){
    if(!confirm("Are you sure?")){
        return;
    }
    const response = await fetch('/thingsnottodo/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({"type" : "softclear"})
    });
    const data = await response.json();
    if(data.error){
        alert("Error: " + data.error);
        return;
    }
}
getNew();