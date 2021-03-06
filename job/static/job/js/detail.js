var canSubmitPledge = true;
var canSubmitWork = true;
var updates_num_searches = 0;
var pledges_num_searches = 0;
var workers_num_searches = 0;
var updates_sort = 'date-descending';
var pledging_sort = 'pledging-descending';
var working_sort = 'working-ascending';

$('document').ready(function() {
    fixHeader();
    $(window).resize(function() {
        fixHeader();
    });
    $('.table-header').click(function() {
        var cls = $(this).parent().attr('class');
        setRowToZero(cls.split('-')[0]);
        prepareToAddRows(cls, 0);
    });
    $('tbody').scroll(function() {
        var cls = $(this).parent().attr('class');
        var table = cls.split('-')[0];
        var total = $('#' + table + '-total').text();
        if ($(this).scrollTop() + $(this).height() === $(this)[0].scrollHeight && $(this).children().count() < total) {
            if (cls !== '') {
                var rows = addToNumRows(cls);
                prepareToAddRows(cls, rows);
            }// end if
        }// end if
    });
});

function fixHeader() {
    var updatesWidth = $('#updates').find('thead').width() - 17;
    $('#updates').find('thead').find('.updates-username').width(0.5 * updatesWidth - 16);
    $('#updates').find('thead').find('.updates-date').width(0.5 * updatesWidth + 1);
    var pledgeWorkWidth = $('#pledging').find('thead').width() - 17;
    $('#pledging').find('thead').find('.pledging-username').width(0.25 * pledgeWorkWidth - 16);
    $('#pledging').find('thead').find('.pledging-date').width(0.25 * pledgeWorkWidth - 16);
    $('#pledging').find('thead').find('.pledging-pledging').width(0.25 * pledgeWorkWidth - 16);
    $('#pledging').find('thead').find('.pledging-paid').width(0.25 * pledgeWorkWidth + 1);
    $('#working').find('thead').find('.working-username').width(0.25 * pledgeWorkWidth - 16);
    $('#working').find('thead').find('.working-started').width(0.25 * pledgeWorkWidth - 16);
    $('#working').find('thead').find('.working-finished').width(0.25 * pledgeWorkWidth - 16);
    $('#working').find('thead').find('.working-received').width(0.25 * pledgeWorkWidth + 1);
}// end fixHeader()

function addToNumRows(table) {
    var rows;
    if (table === 'updates') {
        updates_num_searches = updates_num_searches + 1;
        rows = updates_num_searches;
    } else if (table === 'pledging') {
        pledging_num_searches = pledging_num_searches + 1;
        rows = pledging_num_searches;
    } else if (table === 'working') {
        working_num_searches = working_num_searches + 1;
        rows = working_num_searches;
    }// end if
    return rows;
}// end addToNumRows()

function setRowToZero(table) {
    if (table === 'updates') {
        updates_num_searches = 0;
    } else if (table === 'pledging') {
        pledging_num_searches = 0;
    } else if (table === 'working') {
        working_num_searches = 0;
    }// end if
}// end setRowToZero()

function prepareToAddRows(cls, rows) {
    var table = cls.split('-')[0];
    var type = cls.split('-')[1];
    add_rows_to_tables(rows, table, type, setSortVariable(table, type).split('-')[1]);
}// end prepareToAddRows()

function setSortVariable(table, type) {
    var sort = null;
    if (table === 'updates') {
        if (type === updates_sort.split('-')[0]) {
            if (updates_sort.split('-')[1] === 'ascending') {
                updates_sort = type + '-descending';
            } else {
                updates_sort = type + '-ascending';
            }// end if-else
        } else {
            updates_sort = type + '-ascending';
        }// end if-else
        sort = updates_sort;
    } else if (table === 'pledging') {
        if (type === pledging_sort.split('-')[0]) {
            if (pledging_sort.split('-')[1] === 'ascending') {
                pledging_sort = type + '-descending';
            } else {
                pledging_sort = type + '-ascending';
            }// end if-else
        } else {
            pledging_sort = type + '-ascending';
        }// end if-else
        sort = pledging_sort;
    } else if (table === 'working')  {
        if (type === working_sort.split('-')[0]) {
            if (working_sort.split('-')[1] === 'ascending') {
                working_sort = type + '-descending';
            } else {
                working_sort = type + '-ascending';
            }// end if-else
        } else {
            working_sort = type + '-ascending';
        }// end if-else
        sort = working_sort;
    }// end if
    return sort;
}// end setSortVariable()

function add_rows_to_tables(num_searches, table, column, order) {
    $.ajax({
        url : 'sort',
        data : {
            'num_searches' : num_searches,
            'table' : table,
            'column' : column,
            'order' : order,
        },
        success: function(json) {
            if (json.length > 0) {
                if (table === 'updates') {
                    if (updates_num_searches == 0) $('#updates tbody').empty();
                    addRowsToUpdatesTable(json);
                } else if (table === 'pledging') {
                    if (pledging_num_searches == 0) $('#pledging tbody').empty();
                    addRowsToPledgingTable(json);
                } else if (table === 'working') {
                    if (working_num_searches == 0) $('#working tbody').empty();
                    addRowsToWorkingTable(json);
                }// end if
            }// end if
        },
    });
}// end sort()

function addRowsToUpdatesTable(json) {
    for (var index = 0; index < json.length; index++) {
        var update = json[index];
        var img = '';
        if (update['images'] > 0) img = "<a href='/update/" + update['random_string'] + "/images'>Images</a>";
        var string = "<tr>";
        string = string + "<td class='updates-username'><a href='" + update['username'] + "'>" + update['username'] + "</a></td>";
        string = string + "<td class='updates-date'>" + update['date'] + "</td>";
        string = string + "</tr>";
        string = string + "<tr>";
        string = string + "<td class='updates-comment' coslpan='3'>" + update['comment'];
        string = string + "<span class='images'>" + img + "</span></td>";
        string = string + "</tr>";
        $('#updates tbody').append(string);
    }// end for
}// end addRowsToUpdatesTable()

function addRowsToPledgingTable(json) {
    for (var index = 0; index < json.length; index++) {
        var pledge = json[index];
        var string = "<tr>";
        string = string + "<td class='pledging-username'><a href='"+ pledge['username'] + "'>" + pledge['username'] + "</a></td>";
        string = string + "<td class='pledging-date'>" + pledge['date'] + "</td>";
        string = string + "<td class='pledging-pledging'>" + changeNumberToCurrency(pledge['pledging']) + "</td>";
        string = string + "<td class='pledging-paid'>" + changeNumberToCurrency(pledge['paid']) + "</td>";
        string = string + "</tr>";
        $('#pledging tbody').append(string);
    }// end for
}// end addRowsToPledgesTable()

function addRowsToWorkingTable(json) {
    for (var index = 0; index < json.length; index++) {
        var worker = json[index];
        var finished = worker['finished'];
        if (finished == '01/1/3000') {
            finished = 'N/A';
        }
        var string = "<tr>";
        string = string + "<td class='working-username'><a href='" + worker['username'] + "'>" + worker['username'] + "</a></td>";
        string = string + "<td class='working-started'>" + worker['started'] + "</td>";
        string = string + "<td class='working-finished'>" + finished + "</td>";
        string = string + "<td class='working-received'>" + changeNumberToCurrency(worker['received']) + "</td>";
        string = string + "</tr>";
        $('#working tbody').append(string);
    }// end for
}// end addRowsToPledgesTable()
