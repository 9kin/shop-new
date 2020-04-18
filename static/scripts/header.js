let prev_val = "";

function makeSearch() {
    let value = $("input#q")[0].value;
    if (value == prev_val) {
        return;
    }
    else {
        prev_val = value;
    }


    $.ajax({
        type: "GET",
        url: "/api/search",
        data: {
            "q": value,
        },
        beforeSend: function() {
        },
        success: function(data) {
            console.log(data);
            let items = data["items"];
            let bigcode = "";

            for (const name in items) {
                let cost = items[name]["cost"];
                let count = items[name]["count"];
                let id = items[name]["id"];
                let img = items[name]["img"];
                let code = "";

                code += '<div class="card">';
                code += '<img class="card-img-top" src="/static/img/';
                code += img;
                code += '" alt="Card image cap">';
                code += '<div class="card-body">';
                code += '<i class="fas fa-faucet"></i>';
                code += '<h5 class="card-title">';
                code += name;
                code += '</h5><p class="card-text">';
                code += cost;
                code += ' Осталось ';
                code += count;
                code += '</p><div class="text-center"><a href="#" class="btn"></a></div></div></div>';

                bigcode += code;
            }

            $("div.container")[0].innerHTML = bigcode;
        },
        error: function(error) {
            console.error(error);
        },
        complete: function() {
        },
    });
}

function addEvents() {
    setInterval(makeSearch, 1000);
}

$(function(){
    prev_val = $("input#q")[0].value;
    addEvents();
});