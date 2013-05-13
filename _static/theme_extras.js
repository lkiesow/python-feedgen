$(document).ready(function() {
	$('.headerlink').each(function( index ) {
		var type = $(this).parent().get(0).nodeName
		if (type == 'H1') {
			var name = $(this).parent().get(0).childNodes[0].data;
			var ln   = $(this).attr('href');
			$('div.apitoc').append('<a href="'+ln+'">'+name+'</a>');
		} else if (type == 'H2') {
			var name = $(this).parent().get(0).childNodes[0].data;
			var ln   = $(this).attr('href');
			$('div.apitoc').append('<a class="h2" href="'+ln+'">'+name+'</a>');
		} else if (type == 'DT') {
			//var name = $(this).parent().text().replace('¶', '');
			var name = $(this).parent().html().replace(/<a .*<\/a>/g, '')
				.replace(/<tt class="desc/g, '<span class="apiln')
				.replace(/<\/tt>/g, '</span>');
			var ln   = $(this).attr('href');
			var p = $(this).parent().parent();
			if ( p.hasClass('method') || p.hasClass('attribute') ) {
				$('div.apitoc').append('<a class="partOfClass" href="'+ln+'">'+name+'</a>');
			} else {
				$('div.apitoc').append('<a class="second" href="'+ln+'">'+name+'</a>');
			}
		} else {
			// alert( type );
		}
	});
});
