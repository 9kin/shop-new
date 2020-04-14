$(function(){
    /*$.ajax({
        type: "GET",
        url: "/api/category",
        data: {
            "path": "",
        },
        beforeSend: function() {
            console.log("beforeSend");
        },
        success: function(list_of_messages) {
            console.log(list_of_messages["categories"]);

            /*
            {
                "first" : {
                    "path" : "1",
                    "subfirst" : {
                        "path" : "1.1",
                    },
                    "subfirst" : {
                        "path" : "1.2",
                    },
                },
                "second" : {
                    "path" : "2",
                    "subsecond" : {
                        "path" : "2.1",
                        "subsubsecond" : {
                            "path" : "2.1.1",
                        },
                        "subsubsecond" : {
                            "path" : "2.1.2",
                        },
                    },
                    "subsecond" : {
                        "path" : "2.2",
                    },
                },
            }

            let res = {};
            let cat = list_of_messages["categories"];
            for (let i in cat) {
                console.log(i + ": " + cat[i]);

                let arr = i.split(".");
                let currres = res;
                for (let j = 0; j < arr.length; ++j) {
                    if (j = arr.length - 1) {
                        res[cat[i]] = {
                            "path": i
                        }
                    }
                }
            }*\/
        },
        error: function(error) {
            console.error(error);
        },
        complete: function() {
        },
    });*/

    let fullpath = window.location.href.split("/");
    fullpath = fullpath[fullpath.length-1];
    let fpath = fullpath.split(".");

    console.log(fpath);

    let path = [fpath[0]];
    for (let i = 1; i < fpath.length; i++) {
        path.push(path[i-1] + "-" + fpath[i]);
    }

    console.log(path);

    for (let i = 0; i < path.length; i++) {
        $inp = $("#" + path[i]);
        $inp.prop('checked', true);
        $inp.prop('class', "here");
    }

    $($('.drop-end > a[href="/items/'+fullpath+'"]')[0].parentElement).prop('class', 'drop-end here');
});