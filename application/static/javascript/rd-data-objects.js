/**
 * Created by Tom.Ridd on 08/05/2017.
 */


function barchartObject(data, primary_column, secondary_column,
                        chart_title, x_axis_label, y_axis_label) {
    dataRows = _.clone(data);
    headerRow = dataRows.shift();

    if(secondary_column === '[None]') {
        return barchartSingleObject(headerRow, dataRows, primary_column, chart_title, x_axis_label, y_axis_label);
    } else {
        return barchartDoubleObject(headerRow, dataRows, primary_column, secondary_column, chart_title, x_axis_label, y_axis_label);
    }
}

function barchartSingleObject(headerRow, dataRows, category, chart_title, x_axis_label, y_axis_label) {
    valueIndex = headerRow.indexOf('Value');
    categoryIndex = headerRow.indexOf(category);
    categories = uniqueDataInColumn(dataRows, categoryIndex);

    values = [];
    for(c in categories) {
        values.push(valueForCategory(dataRows, categoryIndex, valueIndex, categories[c]));
    }

    return {
        'type':'bar',
        'title':{'text':chart_title},
        'xAxis':{'title':{'text':x_axis_label}, 'categories':categories},
        'yAxis':{'title':{'text':y_axis_label}},
        'series': [{'name':category, 'data': values}]}
}

function valueForCategory(dataRows, categoryIndex, valueIndex, categoryValue, chart_title, x_axis_label, y_axis_label) {
    for(r in dataRows) {
        if(dataRows[r][categoryIndex] === categoryValue) {
            return parseFloat(dataRows[r][valueIndex]);
        }
    }
    return 0;
}

function barchartDoubleObject(headerRow, dataRows, category1, category2, chart_title, x_axis_label, y_axis_label) {
    valueIndex = headerRow.indexOf('Value');
    categoryIndex = headerRow.indexOf(category1);
    categories = uniqueDataInColumn(dataRows, categoryIndex);

    seriesIndex = headerRow.indexOf(category2);
    series = uniqueDataInColumn(dataRows, seriesIndex);

    seriesData = [];
    for(s in series) {
        seriesRows = _.filter(dataRows, function(row) { return row[seriesIndex] === series[s];});
        values = [];
        for(c in categories) {
            values.push(valueForCategory(seriesRows, categoryIndex, valueIndex, categories[c]));
        }
        seriesData.push({'name':series[s], 'data': values});
    }

    return {
        'type':'bar',
        'title':{'text': chart_title},
        'xAxis':{'title':{'text':x_axis_label}, 'categories':categories},
        'yAxis':{'title':{'text':y_axis_label}},
        'series': seriesData};
}

function uniqueDataInColumn(data, index) {
    values = _.map(data.slice(start = 0), function(item) {
        return item[index]; });
    return _.uniq(values).sort();
}


function linechartObject(data, categories_column, series_column, chart_title, x_axis_label, y_axis_label) {
    dataRows = _.clone(data);
    headerRow = dataRows.shift();

    valueIndex = headerRow.indexOf('Value');
    categoryIndex = headerRow.indexOf(categories_column);
    categories = uniqueDataInColumn(dataRows, categoryIndex);

    seriesIndex = headerRow.indexOf(series_column);
    seriesNames = uniqueDataInColumn(dataRows, seriesIndex);

    chartSeries = [];
    for(s in seriesNames) {
        seriesName = seriesNames[s];
        values = [];
        for(c in categories) {
            category = categories[c];
            values.push(valueForCategoryAndSeries(dataRows, categoryIndex, category, seriesIndex, seriesName, valueIndex));
        }
        chartSeries.push({'name':seriesName, 'data':values});
    }

    return {
        'type':'line',
        'title':{'text':chart_title},
        'xAxis':{'title':{'text':x_axis_label}, 'categories':categories},
        'yAxis':{'title':{'text':y_axis_label}},
        'series': chartSeries};
}

function valueForCategoryAndSeries(dataRows, categoryIndex, categoryValue, seriesIndex, seriesValue, valueIndex) {
    for(r in dataRows) {
        if((dataRows[r][categoryIndex] === categoryValue) && (dataRows[r][seriesIndex] === seriesValue)) {
            return parseFloat(dataRows[r][valueIndex]);
        }
    }
    return 0;
}





function componentChartObject(data, grouping_column, series_column, chart_title, x_axis_label, y_axis_label) {
    dataRows = _.clone(data);
    headerRow = dataRows.shift();

    valueIndex = headerRow.indexOf('Value');
    groupingIndex = headerRow.indexOf(grouping_column);
    groups = uniqueDataInColumn(dataRows, groupingIndex);

    seriesIndex = headerRow.indexOf(series_column);
    seriesNames = uniqueDataInColumn(dataRows, seriesIndex);

    chartSeries = [];
    for(s in seriesNames) {
        seriesName = seriesNames[s];
        values = [];
        for(g in groups) {
            group = groups[g];
            values.push(valueForCategoryAndSeries(dataRows, groupingIndex, group, seriesIndex, seriesName, valueIndex));
        }
        chartSeries.push({'name':seriesName, 'data':values});
    }

    return {
        'type':'component',
        'title':{'text':chart_title},
        'xAxis':{'title':{'text':x_axis_label}, 'categories':groups},
        'yAxis':{'title':{'text':y_axis_label}},
        'series': chartSeries};
}


function simpleTableObject(data, row_column, group_column, data_columns) {

    if(group_column === '[None]') {
        return simpleTable(data, row_column, data_columns);
    } else {
        return groupedTable(data, row_column, group_column, data_columns);
    }
}

function simpleTable(data, category_column, data_columns) {
    var dataRows = _.clone(data);
    var headerRow = dataRows.shift();

    var columnIndex = headerRow.indexOf(category_column);
    var data_column_indices = _.map(data_columns, function(data_column) { return headerRow.indexOf(data_column); });

    var data = _.map(dataRows, function(item) {
        console.log(item);
        return {'category':item[columnIndex],'values':_.map(data_column_indices, function(i) { return item[i]})};
    });

    return {
        'type':'simple',
        'title':{'text':'Simple Table'},
        'category':category_column,
        'columns': data_columns,
        'data': data};
}

function groupedTable(data, category_column, group_column, data_columns) {
    var dataRows = _.clone(data);
    var headerRow = dataRows.shift();

    var columnIndex = headerRow.indexOf(category_column);
    var data_column_indices = _.map(data_columns, function(data_column) { return headerRow.indexOf(data_column); });

    var group_column_index = headerRow.indexOf(group_column);
    var group_values = uniqueDataInColumn(dataRows, group_column_index);

    var group_series = _.map(group_values, function(group) {
        var group_data = _.filter(dataRows, function(item) { return item[group_column_index] === group;});
        var group_data_items = _.map(group_data, function(item) {
            return {'category':item[columnIndex], 'values':_.map(data_column_indices, function(i) { return item[i]})}
        });
        return {'group':group, 'data':group_data_items};
    });

    return {
        'type':'grouped',
        'category': category_column,
        'title':{'text':'Grouped Table'},
        'columns':data_columns,
        'groups': group_series};
}