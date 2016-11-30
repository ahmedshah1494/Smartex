commentForm = createCommentForm(json[i].pk)
                commentForm.on('submit',function(event){
                    var csrftoken = getCookie('csrftoken');
                    $.ajaxSetup({
                        beforeSend: function(xhr, settings) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                    });
                    console.log(csrftoken)
                    event.preventDefault();
                    var field = $(this).find("#id_content")
                    // console.log($(this).attr("action"));
                    $.post($(this).attr("action"),
                            {content: field.val()},
                            function(data){console.log("posted")})
                    .done(function(data){
                        comments=data[0].fields.comments[data[0].fields.comments.length - 1]
                        console.log(comments);
                        console.log(getDate(comments[3]));                       
                        newComment = createComment(comments[0],
                                                    comments[2],
                                                    getDate(comments[3]),
                                                    comments[1])
                        console.log(data);
                        post = $(document.activeElement).parent().parent().parent().parent().parent().parent()
                        console.log(post)
                        console.log('#post_'+data[0].pk)
                        newComment.appendTo(post)
                    })
                    sendRequestForPosts(stream_type);
                })