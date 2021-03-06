var center;
var numSearches = 0;
var ENTER = 13;
var map;
var markers = [];
var sort = "created-descending";

$('document').ready(function() {
    fixHeader()
    $(window).resize(function() {
        fixHeader()
    });
    $('#search').keydown(function(event) {
        if (event.which == ENTER) {
            search();
        }// end if
    });
    $('#location').keydown(function(event) {
        if (event.which == ENTER) {
            search();
        }// end if
    });
    $('#radius').keydown(function(event) {
        if (event.which == ENTER) {
            search();
        }// end if
    });
    $('.table-header').click(function() {
        var cls = $(this).parent().attr('class');
        setSortAndNumSearches(cls.split("-")[1]);
        get_jobs();
    });
    $('tbody').scroll(function() {
        if ($(this).scrollTop() + $(this).height() === $(this)[0].scrollHeight) {
            if (50 * numSearches <= parseInt($('#num-jobs-found').text())) {
                numSearches = numSearches + 1;
                get_jobs();
            }// end if
        }// end if
    });
});

function fixHeader() {
    var oldTableWidth = $('thead').width();
    var newTableWidth = oldTableWidth - 17;
    $('thead').find('.job-title').width(0.35 * newTableWidth - 16);
    $('thead').find('.job-created').width(0.25 * newTableWidth - 16);
    $('thead').find('.job-pledging').width(0.10 * newTableWidth - 16);
    $('thead').find('.job-paid').width(0.10 * newTableWidth - 16);
    $('thead').find('.job-working').width(0.10 * newTableWidth - 16)
    $('thead').find('.job-finished').width(0.10 * newTableWidth + 1)
}

function setSortAndNumSearches(col) {
    if (sort.split("-")[0] === col) {
        if (sort.split("-")[1] === "descending") {
            sort = sort.split("-")[0] + "-ascending";
        } else {
            sort = sort.split("-")[0] + "-descending";
        }// end if-else
    } else {
        numSearches = 1;
        if (col === "date") {
            sort = col + "-descending";
        } else {
            sort = col + "-ascending";
        }// end if-else
    }// end if-else
}// end setSortAndNumSearches()

function search() {
    $('#latitude').val("");
    $('#longitude').val("");
    clearMarkers();
    numSearches = 1;
    applyLocation();
}// end search()

function get_jobs() {
    $.ajax({
        url : 'job/get-jobs',
        data : {
            'numSearches' : numSearches,
            'search' : $('#search').val(),
            'latitude' : $('#latitude').val(),
            'longitude' : $('#longitude').val(),
            'radius' : getRadius(),
            'sort' : sort,
        },
        success: function(json) {
            if (numSearches == 1) {
                $('tbody').empty();
                clearMarkers();
            }// end if
            addJobsToTable(json);
        },
        error: function () {
            $('#search-error-message').text("Invalid Search");
        },
    });
}// end get_jobs()

function get_total_jobs() {
    $.ajax({
        url : 'job/get-total-jobs',
        data : {
            'search' : $('#search').val(),
            'latitude' : $('#latitude').val(),
            'longitude' : $('#longitude').val(),
            'radius' : getRadius(),
            'sort' : sort,
        },
        success: function(json) {
            $('#num-jobs-found').text(json['total']);
        },
    });
}// end get_total_jobs()

function addJobsToTable(json) {
    $('#search-error-message').text('');
    if (json.length == 0) {
        var string = "<tr>";
        string = string + "<td class='job-title'>No Jobs were found.</td>";
        string = string + "<td class='job-created'></td>";
        string = string + "<td class='job-pledging'></td>";
        string = string + "<td class='job-paid'></td>"
        string = string + "<td class='job-working'></td>";
        string = string + "<td class='job-finished'></td>"
        string = string + "</tr>";
        $('tbody').append(string);
    } else {
        for (var index = 0; index < json.length; index++) {
            var job = json[index];
            var string = "<tr>";
            string = string + "<td class='job-title'><a id='" + job["random_string"] + "' href='job/" + job["random_string"] + "'></a></td>";
            string = string + "<td class='job-created'>" + job['date'] + "</td>";
            string = string + "<td class='job-pledging'>$" + turnMoneyToString(job['pledging']) + "</td>";
            string = string + "<td class='job-paid'>$" + turnMoneyToString(job['paid']) + "</td>"
            string = string + "<td class='job-working'>" + job['working'] + "</td>";
            string = string + "<td class='job-finished'>" + job['finished'] + "</td>"
            string = string + "</tr>";
            $('tbody').append(string);
            $('#' + job["random_string"]).text(job["title"]);
            addMarker(new google.maps.LatLng(job['latitude'], job['longitude']), 'job/' + job["random_string"]);    
        }// end for
        if ($('#location').val() !== "") {
            addBounds();
        }// end if
    }// end if-else
}// end addJobsToTable()

function applyLocation() {
    var address = $('#location').val();
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ 'address': address}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            center = results[0].geometry.location;
            $('#latitude').val(center.lat());
            $('#longitude').val(center.lng());
            //map.setCenter(center)
            get_jobs();
            get_total_jobs();
        } else {
            get_jobs();
            get_total_jobs();
        }// end if-else
    });
}// end applyLocation()

function initMap() {
    /*
    map = new google.maps.Map(document.getElementById('map'));
    var bounds = new google.maps.LatLngBounds();
    bounds.extend({lat: 25.7617, lng: -80.1918});
    bounds.extend({lat: 32.7157, lng: -117.1611});
    bounds.extend({lat: 21.9, lng: -160.2});
    bounds.extend({lat: 71.3, lng: -156.8});
    map.fitBounds(bounds);
    */
    search();
}// end initMap()

function addBounds() {
    map.setZoom(1);
    var bounds = new google.maps.LatLngBounds();
    for (var i = 0; i < markers.length; i++) {
        bounds.extend(markers[i].position);
    }// end for
    map.fitBounds(bounds);
    if (map.zoom > 15) map.setZoom(15);
}// end addBounds()

function addMarker(location, url) {
    var marker = new google.maps.Marker({
        position: location,
        map: map,
        url: url,
    });
    google.maps.event.addListener(marker, 'click', function() {
        window.location.href = this.url;
    });
    markers.push(marker);
}// end addMarker()

function setMapOnAll(map) {
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(map);
    }// end for
}// end setMapOnAll()

function clearMarkers() {
    setMapOnAll(null);
}// end clearMarkers()

function deleteMarkers() {
    clearMarkers();
    markers = [];
}// end deleteMarkers()

function getRadius() {
    var radius = $('#radius').val();
    if (radius == '') {
        radius = 10;
        $('#radius-error').text('');
    } else if (isNaN(radius)) {
        $('#radius-error').text('Please enter a valid number.');
    } else {
        $('#radius-error').text('');
    }// end if-else
    return radius;
}// end getRadius()

function turnMoneyToString(number) {
    parts = number.toString().split('.');
    if (parts.length == 1) {
        number = number.toString() + ".00";
    } else {
        if (parts[1].length == 1) {
            number = number.toString() + "0";
        }// end if
    }// end if-else
    return number.toString();
}// end turnMoneyToString()