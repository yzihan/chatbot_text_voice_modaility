const wrapMessagesIntoList = (messages) => {
    const res = [];
    for (let key in messages){
        for(let item of messages[key]){
            res.push(item);
        }
    }
    return res;
}



  const messages = {
      "1":[
        { "role":"assistant", "content":"1"},
        { "role":"user", "content":"2"},
      ],
        "2":[
        { "role":"assistant", "content":"3"},
        { "role":"user", "content":"4"},
      ],
        "3":[
        { "role":"assistant", "content":"5"},
        { "role":"user", "content":"6"},
      ],
        "4":[
        { "role":"assistant", "content":"7"},
        { "role":"user", "content":"8"},
      ],
        "5":[
        { "role":"assistant", "content":"9"},
        { "role":"user", "content":"10"},
      ],
    };
    
  const results = wrapMessagesIntoList(messages);
  console.log(results);
