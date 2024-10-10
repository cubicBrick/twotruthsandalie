document.getElementById("submit").addEventListener("click", submit);

async function submit(){
    const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "username" : document.getElementById('username').value, "password" : document.getElementById('password').value })
    });
    const data = await response.json();
}