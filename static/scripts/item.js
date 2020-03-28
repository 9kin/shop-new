$(document).ready(function() {
    $('#list').click(function(event){
    	event.preventDefault();
    	console.log($('#products .item'));

    	$('#products .item').removeClass('grid-group-item');
    	$('#products .item').addClass('list-group-item');
    	if (window.console) console.log($('#products .item'));
    });
    $('#grid').click(function(event){
    	event.preventDefault();
    	console.log($('#products .item'));
    	
    	$('#products .item').removeClass('list-group-item');
    	$('#products .item').addClass('grid-group-item');

    	if (window.console) console.log($('#products .item'));
    });

    
});

