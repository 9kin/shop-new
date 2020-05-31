$(function(){
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