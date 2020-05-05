$(function() {
    /* === what is this? === */
    $('#list').on("click", function(event){
    	event.preventDefault();
    	console.log($('#products .item'));

    	$('#products .item').removeClass('grid-group-item');
    	$('#products .item').addClass('list-group-item');
    	console.log($('#products .item'));
    });
    $('#grid').on("click", function(event){
    	event.preventDefault();
    	console.log($('#products .item'));
    	
    	$('#products .item').removeClass('list-group-item');
    	$('#products .item').addClass('grid-group-item');

    	console.log($('#products .item'));
    });
    /* =============== */
});

