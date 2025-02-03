async function getThings(){
    const response = await fetch('/thingsnottodo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})
    });
    const data = await response.json();
    const things = data.things;
    return things;
}
async function populate(){
    html = "<tr>\n<td>Number   </td>\n<td>Thing</td>\n</tr>\n";
    const things = await getThings();
    for(var i = 0; i < things.length; ++i){
        html += "<tr><td>";
        html += things[i][0];
        html += "</td>\n<td>";
        html += things[i][1];
        html +="</td></tr>\n";
    }
    document.getElementById("main").innerHTML = html;
    return html;
}
populate();