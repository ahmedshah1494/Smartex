var suppLanguages = {
  'English': 'en',
  'Spanish': 'es',
  'French' : 'fr',
}

function languageList(){
  select = $('<select />')
  opt = $('<option />').attr("language", "null").html("Select Language")
  select.append(opt)
  for (var lang in suppLanguages){
    console.log(suppLanguages[lang])
    opt = $('<option />').attr("language", suppLanguages[lang]).html(lang)
    select.append(opt)
  }
  select.attr("id","languages")
  select.change(function(){
    lang = $("#languages :selected").attr("language")
    if (lang != 'null'){
      console.log(lang)
      translate(lang)
      $("#languages :selected").removeAttr('selected')    
    }
  })
  return select
}

function translate(lang){
  range = editor.getSelection();
  text = editor.getText(range.index, range.length)
  console.log(text);

  $.ajax("/translate/"+text+'/'+lang, {dataType: 'json'})
        .done(function(json){
          translation = (json.data.translations[0].translatedText)
          console.log(translation)
          editor.deleteText(range.index, range.length)
          editor.insertText(range.index, translation)
        })

}