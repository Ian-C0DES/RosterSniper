
$(function () {
	$('#q, #sidebar-col input').keypress(e => { if (e.keyCode === 13) update_courses() });
	$('#days > button').tooltip({delay: {show: 1500, hide: 100}});

	const searchParams = new URLSearchParams(window.location.search);
	searchParams.forEach(function(value, key) {
		if (key === "days") {
			$('#days').children().each(function() {
				if (value.includes(this.innerHTML)) $(this).addClass('active');
			});
		} else {
			$("#" + key).val(value);
		}
	});

	update_courses();
})

function update_courses() {
	const searchParams = new URLSearchParams();

	// URL without query string
	const url = window.location.pathname.split('?')[0]

	$("#term, #sidebar-col input, #q").each(function () {
		if (x = $(this).val().trim()) searchParams.append($(this).attr('id'), x);
	});

	let days = '';
	$('#days > button').each(function () {
		if ($(this).hasClass('active')) days += this.innerHTML;
	});
	if (days) searchParams.append("days", days);

	// Don't allow empty searches (term will always be present)
	if ([...searchParams].length < 2) {
		if (!$('#courses-col').hasClass('bear')) {
			$('#courses-col').addClass('bear');
			$('#courses').html('');
			history.pushState(null, '', url);
		}
		return;
	} // else..

	let params = searchParams.toString()
	$('#courses-col').removeClass('bear');
	history.pushState(null, '', url + '?' + params);
	$.getJSON(`/${url.split('/')[1]}/get-courses/?${params}`).done(
		response => {
			$('#courses').html(response['courses']);
			$('.meeting > span').tooltip({delay: {show: 1500, hide: 100}});
			$('#courses .card-footer button').click(show_all);
			$('#courses td i.fa-star').on('click', favorite);
		}
	);

	$('main').removeClass('sidebar-open');
}

function show_all() {
	$(this).parent().prev().children().eq(1).removeClass('limit-four');
	$(this).parent().remove();
}

function favorite() {

	let clicked = $(this);

	// Toggles the classes between (font awesome) regular and solid
	// Solid -> favorited
	clicked.toggleClass('far fas');

	if (logedin) {
		$.get('/my-courses/', {
			term: $("#term").val(),
			crn: clicked.attr('id'),
			favorite: clicked.hasClass('fas')
		});
	} else {
		window.location.href = '/login/'
	}
}

function sidebar() {
	 $('main').toggleClass('sidebar-open');
}
