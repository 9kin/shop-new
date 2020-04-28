function loadSubcat(obj) {
    let cat_id = $(obj)[0]["name"];
    let $obb = $($("div.undercat")[cat_id-1]);
    console.log($obb);

    $.ajax({
        type: "GET",
        url: "/api/category",
        data: {
            "path": cat_id,
        },
        beforeSend: function() {
            $obb.html("<img src='static/img/load.gif'>");
        },
        success: function(list_of_messages) {
            $obb.html("");
            let subcat = list_of_messages["categories"];
            for(let id in subcat) {
                $obb.append("<a href='/items/"+cat_id+"."+id+"'>"/*+id+": "*/+subcat[id]+"</a>");
            }
        },
        error: function(error) {
            $obb.html("<h1 style='color: darkred;'>ERROR!</h1>");
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