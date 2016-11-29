var editor;
var contextDelim = '\n'
var general_info_cards = new Queue();
console.log(general_info_cards);
var lastSentence = ''
var number_cards_displayed = 3;
var chat_socket;
function getCookie(name) {  
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getDate(jsonDate){
    var months = ["Jan", "Feb", "Mar", "Apr", "May",
                    "Jun", "Jul", "Aug", "Sep", "Oct",
                    "Nov", "Dec"]
    date = new Date(jsonDate)
    var tod;
    console.log(date)
    if (Math.floor(date.getUTCHours() / 12) % 2 == 0){
        tod = "a.m."
    }
    else{
        tod = "p.m."
    }
    return months[date.getUTCMonth()]+". "+date.getUTCDate()+". "+date.getUTCFullYear()+". "+(parseInt(date.getUTCHours()%13)+1)+":"+date.getUTCMinutes()+":"+date.getUTCSeconds()+" "+tod
}

function convertHtmlToRtf(html) {
  // source: http://jsfiddle.net/JamesMGreene/2b6Lc/
      if (!(typeof html === "string" && html)) {
          return null;
      }

      var tmpRichText, hasHyperlinks;
      var richText = html;
      var count = 1;
      // Singleton tags
      richText = richText.replace(/<(?:hr)(?:\s+[^>]*)?\s*[\/]?>/ig, "{\\pard \\brdrb \\brdrs \\brdrw10 \\brsp20 \\par}\n{\\pard\\par}\n");
      richText = richText.replace(/<(?:br)(?:\s+[^>]*)?\s*[\/]?>/ig, "{\\pard\\par}\n");

      // Empty tags
      richText = richText.replace(/<(?:p|div|section|article)(?:\s+[^>]*)?\s*[\/]>/ig, "{\\pard\\par}\n");
      richText = richText.replace(/<(?:[^>]+)\/>/g, "");

      // Hyperlinks
      richText = richText.replace(
          /<a(?:\s+[^>]*)?(?:\s+href=(["'])(?:javascript:void\(0?\);?|#|return false;?|void\(0?\);?|)\1)(?:\s+[^>]*)?>/ig,
          "{{{\n");
      tmpRichText = richText;
      richText = richText.replace(
          /<a(?:\s+[^>]*)?(?:\s+href=(["'])(.+)\1)(?:\s+[^>]*)?>/ig,
          "{\\field{\\*\\fldinst{HYPERLINK\n \"$2\"\n}}{\\fldrslt{\\ul\\cf1\n");
      hasHyperlinks = richText !== tmpRichText;
      richText = richText.replace(/<a(?:\s+[^>]*)?>/ig, "{{{\n");
      richText = richText.replace(/<\/a(?:\s+[^>]*)?>/ig, "\n}}}");

      // Start tags
      richText = richText.replace(/<(?:b|strong)(?:\s+[^>]*)?>/ig, "{\\b\n");
      richText = richText.replace(/<(?:i|em)(?:\s+[^>]*)?>/ig, "{\\i\n");
      richText = richText.replace(/<(?:u|ins)(?:\s+[^>]*)?>/ig, "{\\ul\n");
      richText = richText.replace(/<(?:strike|del)(?:\s+[^>]*)?>/ig, "{\\strike\n");
      richText = richText.replace(/<sup(?:\s+[^>]*)?>/ig, "{\\super\n");
      richText = richText.replace(/<sub(?:\s+[^>]*)?>/ig, "{\\sub\n");
      richText = richText.replace(/<(?:p|div|section|article)(?:\s+[^>]*)?>/ig, "{\\pard\n");
      richText = richText.replace(/<\/(?:p|div|section|article)(?:\s+[^>]*)?>/ig, "\n\\par}\n");
      richText = richText.replace(/<\/(?:b|strong|i|em|u|ins|strike|del|sup|sub)(?:\s+[^>]*)?>/ig, "\n}");

      // Strip any other remaining HTML tags [but leave their contents]
      richText = richText.replace(/<(?:[^>]+)>/g, "");

      // Prefix and suffix the rich text with the necessary syntax
      richText =
          "{\\rtf1\\ansi\n" + (hasHyperlinks ? "{\\colortbl\n;\n\\red0\\green0\\blue255;\n}\n" : "") + richText +
          "\n}";

      return richText;
  }

var toolbarOptions = [
  ['bold', 'italic', 'underline', 'strike'],        // toggled buttons
  ['blockquote', 'code-block'],

  [{ 'header': 1 }, { 'header': 2 }],               // custom button values
  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  [{ 'script': 'sub'}, { 'script': 'super' }],      // superscript/subscript
  [{ 'indent': '-1'}, { 'indent': '+1' }],          // outdent/indent
  [{ 'direction': 'rtl' }],                         // text direction

  // [{ 'size': ['small', false, 'large', 'huge'] }],  // custom dropdown
  [{ 'size': [] }],  // custom dropdown
  [{ 'color': [] }, { 'background': [] }],          // dropdown with defaults from theme
  [{ 'font': [] }],
  [{ 'align': [] }],
  ['clean']                                         // remove formatting button
];

function download(text, name, type) {
  var a = document.getElementById("a");
  var file = new Blob([text], {type: type});
  a.href = URL.createObjectURL(file);
  a.download = name;
}

function loadDocument(id){
  console.log(id)
  $.ajax("/load_document/"+id, {dataType: 'json'})
    .done(function(json){
      // $('.ql-editor').html(content);
      // console.log($('.ql-editor').html())
      console.log(json)
      editor.setContents(JSON.parse(json['content']))
      $('#citations').html(json['citations'])
    })
}

function getContext(){
  text = editor.getText(0,editor.getLength());
  context = text.split(contextDelim);
  return context[context.length - 2] 
}
function loadImage(path, width, height, target) {
    $('<img src="'+ path +'">').load(function() {
      $(this).width(width).height(height).appendTo(target);
    }).error(function(){
      console.log("there was no image");
    });
}
function card_exists(card)
{  if (card == undefined){
      return true;
    }
   for (var i = 0 ; i < general_info_cards.length; i++) {

    if (card.result.detailedDescription.articleBody == general_info_cards[i].result.detailedDescription.articleBody){
      return true;
    }
  }
  return false;
}
function clean_previous_cards(newly_added_cards){
    var list_length = $("#general_info div").length/2;// every card has a div within it

    if (list_length <= number_cards_displayed)
    {

      return;

    }
    if (list_length == newly_added_cards) //list_length >= newly_added_cards
    {
      return;
      
    }
    var old_cards = list_length - newly_added_cards;
    var cards_to_remove = list_length - number_cards_displayed;
    if (cards_to_remove > old_cards)
    {
      cards_to_remove = old_cards;
    }
  for (i = 1; i <= cards_to_remove;i++) { 

    $("#general_info div:first").remove();
    general_info_cards.dequeue();
    }
}
function citation_clicked(curr){
  var link = $(curr).prev().find(">:first-child").text();
  addCitation(link);

}
function display_on_suggestions(suggestion_response){

//________________________________GENERAL INFO SECTION ________________________________  
if (typeof(suggestion_response['general info']) != "undefined")
{
  console.log(suggestion_response['general info'])
  var cards_list_input = suggestion_response['general info'].length;
  var cards_list = $("#general_info");
  
  var newly_added_cards = 0;
  for (var i = 0 ; i < cards_list_input; i++) {
      var  general_info_json = suggestion_response['general info'][i][0];
      if (general_info_json == undefined){
        continue;
        }
      if (general_info_cards.found(general_info_json.result.detailedDescription.articleBody) == true){
        continue
      }
      else {
        general_info_cards.enqueue(general_info_json.result.detailedDescription.articleBody);
        }

      var general_info_card = $("<div>", {"class": "general_info_card"});
      var general_info_image = document.createElement('span');
      general_info_image.class = ("general_info_image");
      var general_info_data = document.createElement('span');
      general_info_data.class = ("general_info_data");
      var general_info_link = $("<div>", {"class": "general_info_link"});
      var general_info_link_button = $("<button>", {"class": "citation_button", "type":"button",'onclick':"citation_clicked(this)"});
      
      if (typeof(general_info_json.result.image) != 'undefined'){
        loadImage(general_info_json.result.image.contentUrl, 60, 60, general_info_image);      
      }
      general_info_data.append(general_info_json.result.detailedDescription.articleBody);    
      general_info_link.append('<a href = '+ general_info_json.result.detailedDescription.url+'>'+ general_info_json.result.detailedDescription.url+'</a>');
      general_info_link_button.append("Cite");
      general_info_card.append(general_info_image);
      general_info_card.append(general_info_data);
      general_info_card.append(general_info_link);
      general_info_card.append(general_info_link_button);

      var general_info_box = $("#general_info");
      general_info_box.append(general_info_card);
      newly_added_cards++;


  }
  clean_previous_cards(newly_added_cards);
}
//________________________________TEXT REPLACEMENT SECTION ________________________________  
  if (typeof(suggestion_response['replacements']) != "undefined"){
    var text_replacement_list_input = suggestion_response['replacements'];
    var text_replacement_list = $("#text_replacement_list");
    var text_replacement_size = 7;
    var text_replacement_li_kept = text_replacement_size - text_replacement_list_input.length;
    console.log(text_replacement_size);
    if (text_replacement_li_kept <= 0){
      text_replacement_list.html('');
      text_replacement_li_kept = 0;
    }
  
    var list_length = $("#text_replacement_list li").length/2;
    for (i = 0; i < (list_length - text_replacement_li_kept);i++) {
      $('#text_replacement_list li:first').remove();
    }
    for (i = 0; (i < text_replacement_list_input.length && i < text_replacement_size) ; i++) {
      if (text_replacement_list_input[i].length  < 2)
      {
        continue;
      }
      sentence = text_replacement_list_input[i][0] + ' --> ' +  text_replacement_list_input[i][1];
      for(k = 0; k < sentence.length ; k ++){
        sentence = sentence.replace("+", " ");  
      }
      
      exp = text_replacement_list_input[i][2];
      //console.log(sentence);
      var list_elem = document.createElement('li');
      var explanation = document.createElement('p');
      explanation.class =  ("explanation");
      list_elem.class = ("b_sentences");
      list_elem.append(sentence);
      if (!(exp === null)){
        explanation.append(exp);
  
      }
      //comment this out if you don't wan an empty explanation html
      list_elem.append(explanation);
  
      text_replacement_list.append(list_elem);
    }
  }
  //________________________________RELATED LINKS SECTION ________________________________ 
    if (typeof(suggestion_response['links']) != "undefined"){     
        var related_links_list_input = suggestion_response['links'][0];
        if (typeof(related_links_list_input) == 'undefined'){
          related_links_list_input = [];
        }
        //['google.com','yahoo.fr','france24.com', 'cnn.com'];
        var related_links = $("#related_links_list");
        console.log('heres related link list input');
        //console.log(related_links_list_input[0]);
        var related_links_size = 7;
        var related_links_li_kept = related_links_size - related_links_list_input.length;
        //console.log(related_links_li_kept);
        if (related_links_li_kept <= 0){
          related_links.html('');
          related_links_li_kept = 0;
        }
    
      var list_length = $("#related_links_list li").length;
      for (i = 0; i < (list_length - related_links_li_kept);i++) {
        $('#related_links_list li:first').remove();
      }
      for (i = 0; (i < related_links_list_input.length && i < related_links_size) ; i++) {
        var citation_link_button = $("<button>", {"class": "citation_button", "type":"button",'onclick':"citation_clicked(this)"});
        citation_link_button.append("Cite");
        sentence = related_links_list_input[i].link;//['link'];
        related_links.append('<li><a href = '+sentence+'>'+sentence+'</a></li>');
        related_links.append(citation_link_button);
        }
      }
    }


function analyseContext(){
  var current_text = getContext();
  var num_sentences = 3;
  var tokenized_text = current_text.split(".");
  if (lastSentence == tokenized_text[tokenized_text.length - 2]){

    return
  }
  lastSentence = tokenized_text[tokenized_text.length - 2];
  var suggestion_request = [];
  var l = tokenized_text.length;
  for (i = 1; (i <= l && i <=num_sentences); i++) { 
    suggestion_request.push(tokenized_text[l-i]);
  }
  lookup_string = suggestion_request.reverse().join('. ');
  console.log(lookup_string);
  
  // $.ajax("/lookup/"+lookup_string, {dataType: 'json'})
  //       .done(function(json){
  //         display_on_suggestions(json);
  //       });
  
  chat_socket.send(lookup_string);
}

function addCitation(text){
  citationBox = $('#citations')
  citationBox.html((citationBox.html() + text).trim() + '\n')
  console.log(citationBox.html())
}

function citationsToHTML(){
  citationBox = $('#citations')
  console.log(citationBox.html())
  citations = (citationBox.html() + "").split('\n')
  console.log(citations)
  citationList = $('<p>Citations:</p><ul></ul>')
  for (i = 0; i < citations.length ; i ++){
    citationList.append($('<li>'+citations[i]+"</li>"))
  }
  console.log((citationList.prop('outerHTML')))
  return citationList.prop('outerHTML')
}

function saveDocument(){
  console.log($('.ql-editor').html())
  console.log(editor.getContents())
  saveLabel = $('#saveTime')
  if ($('.doc_title').val().length == 0){
    saveLabel.html('Autosave disabled, please enter a title to enable autosave')
    return;
  }
  $.post('/save_document/'+(window.location.href).split('/')[(window.location.href).split('/').length - 1], 
          {content: JSON.stringify(editor.getContents()),
           citations: $('#citations').html(),
           title: $('.doc_title').val()}, 
          function(data){
            console.log("posted")            
            saveLabel.html('Last Save:' + (new Date()))
          })
}

var specialElementHandlers = {
    '#editor': function (element, renderer) {
        return true;
    }
};


$(document).ready(function (){
  var csrftoken = getCookie('csrftoken');
    console.log(csrftoken)
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });

  var options = {
    debug: 'info',
    modules: {
      toolbar: toolbarOptions
    },
    placeholder: 'Compose an epic...',
    theme: 'snow'
  };

  editor = new Quill('#editor', options);
  var downloadButton = $('<span class="ql-formats"><a class="custom_link" href="" id="a">Download</a></span>')
  var saveButton = $('<span class="ql-formats"><a class="custom_link" id="saveButton" href="">Save</a></span>')
  var pdfButton = $('<span class="ql-formats"><a class="custom_link" href="">Download PDF</a></span>')
  
  $('.ql-toolbar').append(saveButton)
  $('.ql-toolbar').append(downloadButton)
  $('.ql-toolbar').append(pdfButton)
  $('.ql-toolbar').append(languageList())

  pdfButton.click(function () {
      var doc = new jsPDF();
      event.preventDefault();
      doc.fromHTML($('.ql-editor').html() + citationsToHTML(), 15, 15, {
          'width': 170,
              'elementHandlers': specialElementHandlers
      });
      doc.save($('.doc_title').val()+'.pdf');
  });


	downloadButton.on('click', function(){
		console.log($('.ql-editor').html())
		console.log(convertHtmlToRtf($('.ql-editor').html()))
		download(convertHtmlToRtf($('.ql-editor').html()) + citationsToHTML(), $('.doc_title').val()+".rtf", 'text/plain')
	})

  saveButton.on('click', function(event){
    event.preventDefault();
    if ($('.doc_title').val().length == 0){
      alert("Please enter a title")
      return;
    }
		saveDocument()
  })

  var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
  // console.log(ws_scheme + '://' + window.location.host + "/editor" + window.location.pathname);
  chat_socket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);
  // requires message to be a json
  chat_socket.onmessage = function(message){
    console.log(message['data']);
    display_on_suggestions(JSON.parse(message['data']));
  }

  setInterval(analyseContext, 3000)
  // setInterval(saveDocument, 5000)
})