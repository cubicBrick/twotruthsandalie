var nav = document.getElementById("mainnav")
nav.innerHTML = "<a href=\"/\">Home</a>\n<a href=\"/twotruthsandalie/home\">Two truths and a lie</a><a href=\"/thingsnottodo\">Things not to do</a>"
async function isAuth(){
    const response = await fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    });
    const data = await response.json();
    if(data.result == "1"){
        nav.innerHTML += "<a href=\"/logout\">Logout</a>"
    }
    else{
        nav.innerHTML += "<a href=\"/login\">Login</a>"
    }
}
isAuth();