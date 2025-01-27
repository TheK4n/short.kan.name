function isUrlValid(userInput) {
  var res = userInput.match(/(http(s)?:\/\/.)[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g);
  if(res == null) {
    return false;
  } else {
    return true;
  }
}

async function postData(url, data) {
  const res = await fetch(url, {
    method: 'post',
    body: data
  });
  return await res.text();
}

async function shortIt(one_time) {
  url = 'http://127.0.0.1:8001/';

  if (one_time) {
    url += '?one-time=true';
  }

  let body_data = document.getElementById("url").value

  if (!isUrlValid(body_data)) {
    alert("Huyevaya url")
    return false
  }
  
  return await postData(url, body_data);
}

async function copyURLToClipboard() {
  let data = document.getElementById("url").value
  navigator.clipboard.writeText(data)
  document.getElementById("url").value = ""

  let btn = document.getElementById("btn1")
  btn.innerHTML = 'Shorten'
  btn.onclick = editBody
}

async function editBody() {
  let div = document.getElementById('url');
  let checkbox_status = document.getElementById('one_time_cb').checked;

  let data = await shortIt(checkbox_status);
  if (!data) {
    return
  }
  div.value = data;
  let btn = document.getElementById("btn1")
  btn.innerHTML = 'Copy'
  btn.onclick = copyURLToClipboard
}

