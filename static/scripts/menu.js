$(function(){
    $.ajax({
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
            }*/
        },
        error: function(error) {
            console.error(error);
        },
        complete: function() {
        },
    });
});