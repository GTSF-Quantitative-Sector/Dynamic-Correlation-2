function customCorrelationMatrix(tckrsList, start, end, step){

  var baseURL = 'https://ic-historical-correlation.herokuapp.com/api/v1/correlation';

  finalList = []
  for (i in tckrsList[0]) {
    if (tckrsList[0][i] !== '') {
      finalList.push(tckrsList[0][i]);
    }
  }
  if (finalList.length === 0) {
    return 'Enter TCKRS ^'
  }

  start = start.toISOString().split('T')[0];
  end = end.toISOString().split('T')[0];

  var data = {
      "tckrs": finalList,
      "start": start,
      "end": end,
      "step": step
  }

  var options = {
    'method' : 'post',
    'contentType': 'application/json',
    'payload' : JSON.stringify(data)
  };
  
  var response = UrlFetchApp.fetch(baseURL, options);
  
  data = JSON.parse(response.getContentText());
 
  if(String(data).substring(0,6) == "Error:"){
    throw(String(data));
  }

  var results = []
  for (var i in data) {
    results.push([])
  }
  var col = 0
  var row = 0
  for (var i in data) {
    row = 0;
    for (var j in data[i]) {
      results[row][col] = data[i][j];
      row++
    }
    col++
  }

  return(results);
}

function historicalData(tckrsList, start, end) {
  var baseURL = 'https://ic-historical-correlation.herokuapp.com/api/v1/historical';

  finalList = []
  for (i in tckrsList[0]) {
    if (tckrsList[0][i] !== '') {
      finalList.push(tckrsList[0][i]);
    }
  }
  if (finalList.length === 0) {
    return 'Enter TCKRS ^'
  }

  start = start.toISOString().split('T')[0];
  end = end.toISOString().split('T')[0];

  var data = {
      "tckrs": finalList,
      "start": start,
      "end": end,
      // "step": step
  }

  var options = {
    'method' : 'post',
    'contentType': 'application/json',
    'payload' : JSON.stringify(data)
  };
  
  var response = UrlFetchApp.fetch(baseURL, options);
  
  data = JSON.parse(response.getContentText());
 
  if(String(data).substring(0,6) == "Error:"){
    throw(String(data));
  }

  // console.log(data)

  var results = []
  row = 0
  for (var i in data[finalList[0]]) {
    console.log(i)
    results.push([])
    results[row][0] = i
    row++
  }
  // console.log(results)
  var col = 1
  var row = 0
  for (var i in data) {
    row = 0;
    for (var j in data[i]) {
      results[row][col] = data[i][j];
      row++
    }
    col++
  }
  // console.log(results)
  return(results);
}
