
function doGet(e) {

  // Sweepstake data
  

  // TESTING
  // var res=JSON.parse('[{"fastest_goal_time": "5th minute"}, [{"owner": "Sisson", "player": "Fabian Sch\\u00e4r", "for_team": "Switzerland", "against_team": "Albania"}], {"biggest_margin_amount": "3 goals"}, [{"total_goals": 3, "against_team": "Turkey", "for_team_score": 3, "owner": "Adam", "for_team": "Spain", "against_team_score": 0}, {"total_goals": 3, "against_team": "Republic of Ireland", "for_team_score": 3, "owner": "Paul", "for_team": "Belgium", "against_team_score": 0}, {"total_goals": 3, "against_team": "Wales", "for_team_score": 0, "owner": "Yozzer", "for_team": "Russia", "against_team_score": 3}], {"golden_team_3": "France", "golden_player_3": "Dimitri Payet", "golden_goals_1": "3", "golden_player_2": "Gareth Bale", "golden_player_1": "\\u00c1lvaro Morata", "golden_team_2": "Wales", "golden_goals_2": "3", "golden_goals_3": "2", "golden_owner_1": "Clarkey", "golden_owner_2": "Pedro", "golden_owner_3": "Davo", "golden_team_1": "Spain"}, [{"dirtiest_team_score": 12, "dirtiest_team": "Albania", "dirtiest_team_yellows": "10", "dirtiest_team_owner": "Adam", "dirtiest_team_reds": "1"}, {"dirtiest_team_score": 10, "dirtiest_team": "Italy", "dirtiest_team_yellows": "10", "dirtiest_team_owner": "Sisson", "dirtiest_team_reds": "0"}, {"dirtiest_team_score": 10, "dirtiest_team": "Romania", "dirtiest_team_yellows": "10", "dirtiest_team_owner": "Yozzer", "dirtiest_team_reds": "0"}, {"dirtiest_team_score": 9, "dirtiest_team": "Austria", "dirtiest_team_yellows": "7", "dirtiest_team_owner": "Fatboy", "dirtiest_team_reds": "1"}, {"dirtiest_team_score": 9, "dirtiest_team": "Iceland", "dirtiest_team_yellows": "9", "dirtiest_team_owner": "Davo", "dirtiest_team_reds": "0"}, {"dirtiest_team_score": 8, "dirtiest_team": "Croatia", "dirtiest_team_yellows": "8", "dirtiest_team_owner": "Paul", "dirtiest_team_reds": "0"}, {"dirtiest_team_score": 8, "dirtiest_team": "Hungary", "dirtiest_team_yellows": "8", "dirtiest_team_owner": "Clarkey", "dirtiest_team_reds": "0"}, {"dirtiest_team_score": 7, "dirtiest_team": "Slovakia", "dirtiest_team_yellows": "7", "dirtiest_team_owner": "Fatboy", "dirtiest_team_reds": "0"}, {"dirtiest_team_score": 7, "dirtiest_team": "Turkey", "dirtiest_team_yellows": "7", "dirtiest_team_owner": "Adam", "dirtiest_team_reds": "0"}, {"dirtiest_team_score": 6, "dirtiest_team": "Poland", "dirtiest_team_yellows": "6", "dirtiest_team_owner": "Clarkey", "dirtiest_team_reds": "0"}]]');

  //Logger.log(e.parameter.data);
  var res = JSON.parse(e.parameter.data); 

  // Remove previous version of this document from Drive and create a new one
  
  /*
  var myDocs = DriveApp.getFilesByName("Sweepstakeresults")
  while (myDocs.hasNext()){
    var thisFile = myDocs.next()
    var idToDelete = thisFile.getId()
    Drive.Files.remove(idToDelete)
  }
  
  doc = DocumentApp.create('Sweepstakeresults');
  */
  
  // Create file if it doesn't exist, otherwise return id
  // Assumes there is only 1 file with this name
  var filename = 'Sweepstakeresults';
  
  function getDoc() {
  
    var docs = DriveApp.getFilesByName(filename);
    if (docs.hasNext()) {
      var file = docs.next();
      return file.getId();
    } else {
      var myDoc = DocumentApp.create(filename);
      return myDoc.getId();
    }
  }
  
  var doc = DocumentApp.openById(getDoc());

  // Remove existing document content ready to update
  
  var body = doc.getBody();
  body.setText("")
  body.clear()

  // Styles
  
  var titleStyle = {};
  titleStyle[DocumentApp.Attribute.HORIZONTAL_ALIGNMENT] = DocumentApp.HorizontalAlignment.CENTER;
  titleStyle[DocumentApp.Attribute.FONT_FAMILY] = 'Georgia';
  titleStyle[DocumentApp.Attribute.BOLD] = true;
  titleStyle[DocumentApp.Attribute.FONT_SIZE] = 26;
  titleStyle[DocumentApp.Attribute.SPACING_BEFORE] = 20;
  
  var headingStyle = {};
  headingStyle[DocumentApp.Attribute.HORIZONTAL_ALIGNMENT] = DocumentApp.HorizontalAlignment.CENTER;
  headingStyle[DocumentApp.Attribute.FONT_FAMILY] = 'Georgia';
  headingStyle[DocumentApp.Attribute.BOLD] = false;
  headingStyle[DocumentApp.Attribute.FONT_SIZE] = 18;
  headingStyle[DocumentApp.Attribute.SPACING_AFTER] = 20;
  headingStyle[DocumentApp.Attribute.SPACING_BEFORE] = 40;
  
  var bodyStyle = {};
  bodyStyle[DocumentApp.Attribute.HORIZONTAL_ALIGNMENT] = DocumentApp.HorizontalAlignment.LEFT;
  bodyStyle[DocumentApp.Attribute.FONT_FAMILY] = 'Arial';
  bodyStyle[DocumentApp.Attribute.BOLD] = false;
  bodyStyle[DocumentApp.Attribute.FONT_SIZE] = 14;
  
  var tablestyle = {};
  tablestyle[DocumentApp.Attribute.BORDER_COLOR] = '#FFFFFF';
  tablestyle[DocumentApp.Attribute.SPACING_AFTER] = 20;
  
  var timeStyle = {};
  timeStyle[DocumentApp.Attribute.HORIZONTAL_ALIGNMENT] = DocumentApp.HorizontalAlignment.CENTER;
  timeStyle[DocumentApp.Attribute.FONT_FAMILY] = 'Arial';
  timeStyle[DocumentApp.Attribute.BOLD] = false;
  timeStyle[DocumentApp.Attribute.FONT_SIZE] = 10;
  timeStyle[DocumentApp.Attribute.SPACING_AFTER] = 200;
  
  // Date
  var m_names = new Array("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec");

  var d = new Date();
  var curr_date = d.getDate();
  var curr_month = d.getMonth();
  var curr_year = d.getFullYear();
  var cur_hour = d.getHours();
  var cur_min = ('0'+d.getMinutes()).slice(-2);
  var now = (curr_date + "-" + m_names[curr_month] + "-" + curr_year + " " + cur_hour + ":" + cur_min);
    
  // TITLE

  body.appendParagraph("Sweepstake scores on the doors")
  .setAttributes(titleStyle);
  body.appendParagraph("Updated: ")
  .setAttributes(timeStyle)
  .appendText(now)
  
  // FASTEST GOAL
  
  var cells = [
   ['Player','{player}'],
   ['Game', '{team} vs {ag_team}'],
   ['Winning','{winner}']
  ];
  
  body.appendParagraph("Fastest Goal")
  .setAttributes(headingStyle);
  
  var section = body.appendParagraph("Time: ")
  .setAttributes(bodyStyle)
  .setSpacingAfter(20)
  .appendText(res[0]['fastest_goal_time']);

  // loop and fill
  
  fastest_goal_results=res[1];
  
  for (i=0; i<fastest_goal_results.length; i++){
    body.appendHorizontalRule();
    body.appendParagraph("");
    var result = fastest_goal_results[i];
    var restable = body.appendTable(cells);
    restable.setAttributes(tablestyle);
    restable.setColumnWidth(0, 150);
    
    for (var key in result){
      if (key === 'player'){
        restable.replaceText('{player}', result[key])
      } else if (key === 'for_team'){
        restable.replaceText('{team}', result[key])
      } else if (key === 'against_team'){
        restable.replaceText('{ag_team}', result[key])
      } else if (key === 'owner'){
        restable.replaceText('{winner}', result[key])
      }
    }
  }
  
  body.appendPageBreak();
  
  // WORST DRUBBING

  var section = body.appendParagraph("Biggest drubbing")
  .setAttributes(headingStyle);
  
  section = body.appendParagraph("Drub factor: ")
  .setAttributes(bodyStyle)
  .setSpacingAfter(20)
  .appendText(res[2]['biggest_margin_amount']);
  
  var cells = [
   ['{for_team}','{for_team_score}'],
   ['{against_team}', '{against_team_score}'],
   ['Winner','{winner}']
  ];

  // loop and fill
  
  biggest_drubbing_results=res[3];
  
  for (i=0; i<biggest_drubbing_results.length; i++){
    body.appendHorizontalRule();
    body.appendParagraph("");
    var result = biggest_drubbing_results[i];
    var restable = body.appendTable(cells);
    restable.setAttributes(tablestyle);
    restable.setColumnWidth(0, 150);
    
    for (var key in result){
      if (key === 'for_team'){
        restable.replaceText('{for_team}', result[key])
      } else if (key === 'for_team_score'){
        restable.replaceText('{for_team_score}', result[key])
      } else if (key === 'against_team'){
        restable.replaceText('{against_team}', result[key])
      } else if (key === 'against_team_score'){
        restable.replaceText('{against_team_score}', result[key])
      } else if (key === 'owner'){
        restable.replaceText('{winner}', result[key])
      }
    }
  }

  body.appendPageBreak();
  
  // GOLDEN BOOT
  
  gold_boot_results=res[4];

  var section = body.appendParagraph("Golden boot")
  .setAttributes(headingStyle);
  
  for (i=1; i<4; i++){
    body.appendParagraph("");
    body.appendParagraph(i);
    body.appendHorizontalRule();
  
    section = body.appendParagraph(gold_boot_results['golden_player_'+String(i)])
    .setAttributes(bodyStyle);
    section = body.appendParagraph(gold_boot_results['golden_team_'+String(i)])
    .setAttributes(bodyStyle);
    section = body.appendParagraph("Goals: ")
    .setAttributes(bodyStyle)
    .setSpacingAfter(20);
    section.appendText(gold_boot_results['golden_goals_'+String(i)])
    section = body.appendParagraph("Winner: ")
    .appendText(gold_boot_results['golden_owner_'+String(i)])
    .setAttributes(bodyStyle);
  }
  
  body.appendPageBreak();
  
  // DIRTIEST TEAM
  
  dirtiest_team_results=res[5];

  var section = body.appendParagraph("Dirtiest team")
  .setAttributes(headingStyle);
  
  for (i=0; i<3; i++){
  
    body.appendParagraph("");
    body.appendParagraph(i+1);
    body.appendHorizontalRule();
    
    section = body.appendParagraph(dirtiest_team_results[i]['dirtiest_team'])
    .setAttributes(bodyStyle);
    section = body.appendParagraph("Red cards: ")
    .setAttributes(bodyStyle);
    section.appendText(dirtiest_team_results[i]['dirtiest_team_reds']);
    section = body.appendParagraph("Yellow cards: ")
    .setAttributes(bodyStyle);
    section.appendText(dirtiest_team_results[i]['dirtiest_team_yellows']);
    section = body.appendParagraph("Score: ")
    .setAttributes(bodyStyle)
    .setSpacingAfter(20);
    section.appendText(dirtiest_team_results[i]['dirtiest_team_score']);
    section = body.appendParagraph("Winner: ")
    .setAttributes(bodyStyle);
    section.appendText(dirtiest_team_results[i]['dirtiest_team_owner']);
  }
  
  return HtmlService.createHtmlOutput("<h2>Script executed</h2>")

}

