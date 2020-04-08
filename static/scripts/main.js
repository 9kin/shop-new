function loadSubcat(obj) {
    let id = $(obj)[0]["name"];
    let $obb = $($("div.undercat")[id-1]);
    console.log($obb);

    $.ajax({
        type: "GET",
        url: "/api/category",
        data: {
            "path": id,
        },
        beforeSend: function() {
            $obb.html("<img src='static/img/load.gif'>");
        },
        success: function(list_of_messages) {
            $obb.html("");
            let subcat = list_of_messages["categories"];
            for(let id in subcat) {
                $obb.append("<a href='/items/"+id+"'>"/*+id+": "*/+subcat[id]+"</a>");
            }
        },
        error: function(error) {
            $obb.html("<p style='color: darkred;'>ERROR!</p>");
            console.error(error);
        },
        complete: function() {
        },
    });
}

function addEvents() {
    $("input.check").on("change", function(){
        if (this.checked) {
            loadSubcat(this);
        }
    });
}

$(function(){
    addEvents();
});